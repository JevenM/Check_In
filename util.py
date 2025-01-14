from PIL import Image
import cv2, numpy as np
from retrying import retry
from selenium import webdriver
import os, sys, time, ddddocr, requests
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from io import BytesIO
import random

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox') # 解决DevToolsActivePort文件不存在的报错
chrome_options.add_argument('window-size=1920x1080') # 指定浏览器分辨率
chrome_options.add_argument('--disable-gpu') # 谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--headless') # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)


def get_web_driver():
    # chromedriver = "/usr/bin/chromedriver"
    chromedriver = "chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_options)
    driver.implicitly_wait(10) # 所有的操作都可以最长等待10s
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browserClientA"}})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    return driver

# 一直等待某元素可见，默认超时10秒（此函数暂时没有使用）
def is_visible(driver, locator, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))
        return element
    except TimeoutException:
        return False

def Ocr_Captcha(driver, locator, img_path): # 验证码识别
    propertery = driver.find_element_by_xpath(locator)
    driver.save_screenshot(img_path)
    img = Image.open(img_path)
    location = propertery.location
    size = propertery.size
    left = location['x']
    top = location['y']
    right = left + size['width']
    bottom = top + size['height']
    image = img.crop((left, top, right, bottom))  # 左、上、右、下
    image.save(img_path)
    ocr = ddddocr.DdddOcr()
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)
    return res

class Track(object):
    # 处理前图片
    slider = "./slider.png"
    background = "./background.png"

    # 将处理之后的图片另存
    slider_bak = "./slider_bak.png"
    background_bak = "./background_bak.png"

    def get_track(self, slider_url, background_url) -> list:
        distance = self.get_slide_distance(slider_url, background_url)
        result = self.gen_normal_track(distance)
        return result

    @staticmethod
    def gen_normal_track(distance):
        def norm_fun(x, mu, sigma):
            pdf = np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))
            return pdf

        result = []
        for i in range(-10, 10, 1):
            result.append(norm_fun(i, 0, 1) * distance)
        result.append(sum(result) - distance)
        return result

    @staticmethod
    def gen_track(distance):  # distance为传入的总距离
        # 移动轨迹
        result = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 1

        while current < distance:
            if current < mid:
                # 加速度为2
                a = 4
            else:
                # 加速度为-2
                a = -3
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            result.append(round(move))
        return result

    @staticmethod
    def onload_save_img(slider_url, slider):
        r = requests.get(slider_url)
        with open(slider, 'wb') as f:
            f.write(r.content)

    def get_slide_distance(self, slider_url, background_url):

        # 下载验证码背景图,滑动图片
        self.onload_save_img(slider_url, self.slider)
        self.onload_save_img(background_url, self.background)
        # 读取进行色度图片，转换为numpy中的数组类型数据
        slider_pic = cv2.imread(self.slider, 0)
        background_pic = cv2.imread(self.background, 0)
        # 获取缺口图数组的形状 -->缺口图的宽和高
        width, height = slider_pic.shape[::-1]

        cv2.imwrite(self.background_bak, background_pic)
        cv2.imwrite(self.slider_bak, slider_pic)
        # 读取另存的滑块图
        slider_pic = cv2.imread(self.slider_bak)
        # 进行色彩转换
        slider_pic = cv2.cvtColor(slider_pic, cv2.COLOR_BGR2GRAY)
        # 获取色差的绝对值
        slider_pic = abs(255 - slider_pic)
        # 保存图片
        cv2.imwrite(self.slider_bak, slider_pic)
        # 读取滑块
        slider_pic = cv2.imread(self.slider_bak)
        # 读取背景图
        background_pic = cv2.imread(self.background_bak)
        # 比较两张图的重叠区域
        result = cv2.matchTemplate(slider_pic, background_pic, cv2.TM_CCOEFF_NORMED)
        # 获取图片的缺口位置
        top, left = np.unravel_index(result.argmax(), result.shape)
        # 背景图中的图片缺口坐标位置
        return left * 340 / 552


# 网易易盾
class CrackSlider:

    def __init__(self, driver):
        # options = webdriver.ChromeOptions()
        # options.add_argument('--ignore-certificate-errors')
        # 不加这一行说明chrome.exe的位置会报错
        # options.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        #self.driver = webdriver.Chrome(chrome_options=options)
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)
        
        self.zoom = 1
        self.tracks = {}
        self.success = 0
        self.unsuccess = 0
        self.targname = ''
        self.tempname = ''
        self.flag = False

    def get_pic(self):
        # 定位到的第一个元素即可，即使页面有多个class也不怕
        # 以下两个条件验证元素是否出现，传入的参数都是元组类型的locator，如(By.ID, ‘kw’) 
        # 顾名思义，一个只要一个符合条件的元素加载出来就通过；另一个必须所有符合条件的元素都加载出来才行 
        # presence_of_element_located 
        # presence_of_all_elements_located
        time.sleep(2)
        # target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img')))
        # template = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_jigsaw')))
        try:
            
            backgroud_img = self.driver.find_element_by_xpath("//*[@class='yidun_bg-img']")[0]
            slide_img = self.driver.find_element_by_xpath("//*[@class='yidun_jigsaw']")[0]
        except:
            self.flag = True
            print("没有图片，直接跳转")
            return
        
        target_link = backgroud_img.get_attribute('src')
        template_link = slide_img.get_attribute('src')
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        self.targname = "target_demo.png"
        self.tempname = 'template_demo.png'
        target_img.save(self.targname)
        template_img.save(self.tempname)
        local_img = Image.open(self.targname)
        size_loc = local_img.size
        print(size_loc[0])
        self.zoom = 260 / int(size_loc[0])

    # def get_tracks(self, distance):
    #     print("distance： %f" % distance)
    #     # 这15个像素是为了与后面back_tracks的距离的和抵消
    #     # distance += 15
    #     v = 0
    #     t = 0.2
    #     forward_tracks = []
    #     current = 0
    #     mid = distance * 4 / 6  #减速阀值
    #     mid2 = distance * 3/15
    #     # 这个加速度公式浪费了我一晚上，最终结论，不是之前物理中学的那个公式，这个是在每个时间段累加的，区别不大
    #     # 但是意义是相同的，不必钻牛角尖。还有a设置为2和3还有3/5和2/5先加速后减速是为了让滑动块刚好在准确位置速度为0，如果把正a改小或者把负a减小都不行，
    #     # 会造成重复运动，比如把下面的注释取消，第二个if改为elif即可。
    #     # 本人已经用公示论证，唉就是这一点我糊涂了。
    #     while current < distance:
    #         if current < mid2:
    #             a = 1.5  
    #         elif current < mid:
    #         	a = 2   #加速度为+2
    #         else:
    #             a = -3  #加速度-3
    #         # print("a为: %f" % a)
    #         s  = v * t + 0.5 * a * (t ** 2)
    #         v = v + a * t
    #         current += s
    #         # print("current为: %f" % current)
    #         forward_tracks.append(round(s))

    #     back_tracks = [-3, -2, -2, -0, -2, -2, 0, -1, -1, -2]
    #     return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}

    def get_tracks(self, distance):
        track = []
        # 当前位移
        current = 0
        # 先加速再匀速再减速
        # 匀速运动的位移量
        # over = random.randint(distance, distance + 10)

        x_1 = float('%.4f' % random.uniform(3 / 5, 6 / 8))

        # x_ac加速变匀速， x_de匀速变减速的点
        x_ac = distance * x_1

        # 计算间隔
        t = 0.2
        # 初速度
        v = random.randint(0, 2)

        while current < distance:
            if current < x_ac:
                a = random.randint(2, 4)
            else:
                a = -random.randint(3, 7)
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t

            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return {'forward_tracks': track}

    def match(self, target, template):
        """
        :param target: target image path
        :param template: template image path
        :return: diatance to slide
        """
        img_rgb = cv2.imread(target, 1)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template, 0)
        '''
        flags = -1：imread按解码得到的方式读入图像
        flags = 0：imread按单通道的方式读入图像，即灰白图像
        flags = 1：imread按三通道方式读入图像，即彩色图像
        '''
        # run = 1
        w, h = template.shape[::-1]
        print("width: %d, height: %d" % (w, h))
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        # result参数表示匹配结果图像，必须是单通道32位浮点。如果image的尺寸为W x H，
        # templ的尺寸为w x h，则result的尺寸为(W-w+1)x(H-h+1)。
        run = 1

        # 使用二分法查找阈值的精确值
        L = 0
        R = 1.0
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            print("threshold: %f" % threshold)
            if threshold < 0:
                print('Error')
                return None

            loc = np.where(res >= threshold)
            # 返回的是数组的列表，如果是二维，则有两个数组，一个是横坐标一个纵坐标
            print("loc[1]的长度为：%d" % len(loc[1]))
            if len(loc[1]) > 1:
                # 大于1说明匹配了多个目标模板，而我们只需要确定一个
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                print('目标区域起点x坐标为：%d' % loc[1][0])
                print('loc[0]为: ', loc[0])
                for i in loc[0]:
                    print(i)
                print('loc[1]为: ', loc[1])
                for j in loc[1]:
                    print(j)
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2
        return loc[1][0]

    def crack_slider(self):
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'yidun_slider')))
        ActionChains(self.driver).click_and_hold(slider).perform()
        print("sum(tracks['forward_tracks']): ", sum(self.tracks['forward_tracks']))
        # 先向前移动
        for track in self.tracks['forward_tracks']:
            ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()

        # time.sleep(0.2)
        # 向后移动
        # for back_tracks in self.tracks['back_tracks']:
        #     ActionChains(self.driver).move_by_offset(xoffset=back_tracks, yoffset=0).perform()
        # 然后前后抖动
        # ActionChains(self.driver).move_by_offset(xoffset=-4, yoffset=0).perform()
        # ActionChains(self.driver).move_by_offset(xoffset=4, yoffset=0).perform()
        time.sleep(0.5)
        # 释放hold操作
        ActionChains(self.driver).release().perform()
        # time.sleep(2)

    def begin(self):
        self.get_pic()
        if self.flag:
            return False
        distance = self.match(self.targname, self.tempname)
        print("zoom： %f" % self.zoom)
        self.tracks = self.get_tracks((distance + 7) * self.zoom)  # 对位移的缩放计算
        self.crack_slider()
        return True


