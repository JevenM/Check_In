from util import *

username = sys.argv[1] # 登录账号
password = sys.argv[2] # 登录密码
img_path = os.getcwd() + "/1.png"


# 本地测试，在anaconda中的base环境安装相应的库，然后执行，成功签到
# 在github上不行，卡死timeout
@retry(stop_max_attempt_number=5)
def ruisi():
    try:
        driver = get_web_driver()
        driver.get("http://rs.xidian.edu.cn/member.php?mod=logging&action=login")
        driver.find_element_by_xpath("/html/body/div[6]/div/div[2]/div/div[2]/div[1]/div[1]/form/div/div[1]/table/tbody/tr/td[1]/input").send_keys(username)
        driver.find_element_by_xpath("/html/body/div[6]/div/div[2]/div/div[2]/div[1]/div[1]/form/div/div[2]/table/tbody/tr/td[1]/input").send_keys(password)

        valid = Ocr_Captcha(driver, "/html/body/div[6]/div/div[2]/div/div[2]/div[1]/div[1]/form/div/span/div/table/tbody/tr/td/span[2]/img", img_path) # 验证码识别
        print(valid)
        driver.find_element_by_xpath("/html/body/div[6]/div/div[2]/div/div[2]/div[1]/div[1]/form/div/span/div/table/tbody/tr/td/input").send_keys(valid)
        driver.find_element_by_xpath("/html/body/div[6]/div/div[2]/div/div[2]/div[1]/div[1]/form/div/div[6]/table/tbody/tr/td[1]/button").click()

        time.sleep(4)
        driver.get("http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign")

        if driver.find_element_by_xpath("/html/body/div[7]/div[2]/div[1]/h1[1]").text == "您今天已经签到过了或者签到时间还未开始":
            print("您今天已经签到过了或者签到时间还未开始")
        else:
            if driver.find_element_by_xpath("//*[@id='kx']") !=[]:
                driver.find_element_by_xpath("//*[@id='kx']").click()
                driver.find_element_by_xpath("//*[@id='todaysay']").send_keys("Hello World!")

            if driver.find_element_by_xpath("//*[@id='qiandao']/table[1]/tbody/tr/td/div/a") !=[]:
                driver.find_element_by_xpath("//*[@id='qiandao']/table[1]/tbody/tr/td/div/a").click()
                print('ruisi签到成功')
            else:
                print("ruisi签到失败")
    except:
        print("ruisi签到异常")
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    ruisi()
