from util import *

username = sys.argv[1] # 登录账号
password = sys.argv[2] # 登录密码
img_path = os.getcwd() + "/1.png"

@retry(stop_max_attempt_number=5)
def ruisi():
    try:
        driver = get_web_driver()
        driver.get("http://rs.xidian.edu.cn/member.php?mod=logging&action=login")
        driver.find_element_by_xpath("//*[@id='username_LV9uo']").send_keys(username)
        driver.find_element_by_xpath("//*[@id='password3_LV9uo']").send_keys(password)

        valid = Ocr_Captcha(driver, "//*[@id='vseccode_cSgPZzqZ']/img", img_path) # 验证码识别

        driver.find_element_by_xpath("//*[@id='seccodeverify_cSgPZzqZ']").send_keys(valid)
        driver.find_element_by_xpath("//*[@id='loginform_LV9uo']/div/div[6]/table/tbody/tr/td[1]/button").click()

        time.sleep(4)
        driver.get("http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign")

        driver.find_element_by_xpath("//*[@id='kx']").click()
        
        driver.find_element_by_xpath("//*[@id='todaysay']").send_keys("Hello World!")

        if driver.find_element_by_xpath("//*[@id='qiandao']/table[1]/tbody/tr/td/div/a") !=[]:
            driver.find_element_by_xpath("//*[@id='qiandao']/table[1]/tbody/tr/td/div/a").click()
            print('ruisi签到成功')
        else:
            print("ruisi签到失败")
    except:
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    ruisi()
