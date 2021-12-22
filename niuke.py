from util import *

username = sys.argv[1] # 登录账号
password = sys.argv[2] # 登录密码
img_path = os.getcwd() + "/1.png"


@retry(stop_max_attempt_number=1)
def niuke():
    try:
        driver = get_web_driver()
        driver.get("https://www.nowcoder.com/login?callBack=https://www.nowcoder.com/ta/huawei")

        time.sleep(1)
        path2 = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/ul/li[2]")
        path3 = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/ul/li[3]")

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
        f = track.begin()
        if f is False:
            print("结束")
            return

        time.sleep(4)
        driver.get("https://www.nowcoder.com/ta/huawei")

        try:
            if driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[4]/div[1]/div[1]/a").text == "已打卡":
                print("牛客已打卡")
            else:
                driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[4]/div[1]/div[1]/a").click()
                time.sleep(1)
                driver.find_element_by_xpath("/html/body/div[4]/div[2]/div[1]/div[2]/div[3]/button").click()
            
                print('niuke签到成功')
        except:
            print('niuke签到失败')
            raise
    except:
        print("niuke签到异常")
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    niuke()
