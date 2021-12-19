from util import *

username = sys.argv[1] # 登录账号
password = sys.argv[2] # 登录密码
img_path = os.getcwd() + "/1.png"

@retry(stop_max_attempt_number=5)
def moyupai():
    try:
        driver = get_web_driver()
        driver.get("http://rs.xidian.edu.cn/portal.php")
        driver.find_element_by_xpath("//*[@id='ls_username']").send_keys(username)
        driver.find_element_by_xpath("//*[@id='ls_password']").send_keys(password)
        driver.find_element_by_xpath("//*[@id='lsform']/div/div[1]/table/tbody/tr[2]/td[3]/button").click()

        time.sleep(5)
        valid = Ocr_Captcha(driver, "//*[@id='vseccode_cSAoFi3rx']/img", img_path) # 验证码识别

        driver.find_element_by_xpath("//*[@id='seccodeverify_cSAoFi3rx']").send_keys(valid)
        driver.find_element_by_xpath("//*[@id='loginform_LMDsp']/div/div[2]/table/tbody/tr/td[1]/button").click()

        time.sleep(2)
        driver.get("http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign")

        if driver.find_element_by_xpath("//*[@id='yesterday']") !=[]:
            driver.find_element_by_xpath("//*[@id='yesterday']").click()
            print('moyupai签到成功')
    except:
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    moyupai()
