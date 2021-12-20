from util import *

username = sys.argv[1] # 登录账号
password = sys.argv[2] # 登录密码
img_path = os.getcwd() + "/1.png"


def Sliding_Captcha(driver):
    # 获取验证图片
    slide_img = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[2]/div/div/div/div[1]/div/div[1]/img[2]")
    backgroud_img = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[2]/div/div/div/div[1]/div/div[1]/img[1]")
    slide_url = slide_img.get_attribute("src")
    backgroud_url = backgroud_img.get_attribute("src")
    
    track = CrackSlider()
    result = track.get_track(slide_url, backgroud_url)

    verify_div = driver.find_element(By.XPATH, '''/html/body/div[3]/div[2]/div/div[2]/div/div/div/div[2]/div[2]''')

    # 按下鼠标左键
    ActionChains(driver).click_and_hold(verify_div).perform()
    time.sleep(0.5)
    # 遍历轨迹进行滑动
    for t in result:
        time.sleep(0.01)
        ActionChains(driver).move_by_offset(xoffset=t, yoffset=0).perform()
    # 释放鼠标
    ActionChains(driver).release(on_element=verify_div).perform()
    time.sleep(10)

@retry(stop_max_attempt_number=5)
def niuke():
    try:
        driver = get_web_driver()
        driver.get("https://www.nowcoder.com/login")

        time.sleep(1)
        path2 = self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/ul/li[2]")
        path3 = self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/ul/li[3]")

        # 先切换class的active状态
        driver.execute_script("arguments[0].setAttribute(arguments[1],arguments[2])", path2, 'class','tab-item')
        driver.execute_script("arguments[0].setAttribute(arguments[1],arguments[2])", path3, 'class','tab-item active')
        
        # 点击切换tab
        js = 'document.querySelector("body > div.nk-container > div.account-form-wrapper > div > div.flex-auto.plr-15.pt-5.pb-6 > div:nth-child(2) > div.txt-center.mb-8 > ul > li.tab-item.active").click();'
        driver.execute_script(js)

        driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/form/div[1]/div/div/input").send_keys(username)
        driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/form/div[2]/div/div/input").send_keys(password)
        
        # 点击登录，弹出滑动验证码
        driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/form/button").click()
        
        # 验证码处理，需要重新为网易易盾编写破解程序
        track = CrackSlider(driver) 
        track.begin()

        time.sleep(4)
        driver.get("https://www.nowcoder.com/profile/462482432")

        if driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[4]/a[2]") !=[]:
            driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[4]/a[2]").click()
            print('niuke签到成功')
        else:
            print("niuke签到失败")
    except:
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    niuke()
