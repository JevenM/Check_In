from util import *

username = sys.argv[1] # 登录账号
password = sys.argv[2] # 登录密码
img_path = os.getcwd() + "/1.png"


# 失败 出现了旋转验证码，暂时没有方案
@retry(stop_max_attempt_number=5)
def tieba():
    try:
        driver = get_web_driver()
        driver.get("https://tieba.baidu.com/index.html")
        driver.find_element_by_xpath("//*[@id='com_userbar']/ul/li[4]/div/a").click()
        driver.find_element_by_xpath("//*[@id='TANGRAM__PSP_4__footerULoginBtn']").click()
        time.sleep(1)
        driver.find_element_by_xpath("//*[@id='TANGRAM__PSP_4__userName']").send_keys(username)
        driver.find_element_by_xpath("//*[@id='TANGRAM__PSP_4__password']").send_keys(password)
        driver.find_element_by_xpath("//*[@id='TANGRAM__PSP_4__submit']").click()
        time.sleep(1)
        driver.find_element_by_xpath("//*[@id='onekey_sign']/a").click()
        time.sleep(1)
        if driver.find_element_by_xpath("//*[@id='dialogJbody']/div/div/div[1]/a") != []:
            driver.find_element_by_xpath("//*[@id='dialogJbody']/div/div/div[1]/a").click()
            print("tieba签到成功")
    except:
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    # v2ex()
    tieba()