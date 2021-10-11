from util import *

username = sys.argv[1] # 登录账号
password = sys.argv[2] # 登录密码
img_path = os.getcwd() + "/1.png"

def save_img(src):
    img = requests.get(src)
    with open(img_path, "wb") as f:
        f.write(img.content)
        f.close()

def gamekegs(driver):
    try:

        driver.get("https://gamekegs.com/login")
        driver.maximize_window()
        driver.find_element_by_xpath("//*[@id='username']").send_keys(username)
        driver.find_element_by_xpath("//*[@id='password']").send_keys(password)

        driver.find_element_by_xpath("//*[@class='captcha-clk2']").click() # 点击验证码
        is_visible(driver, "//*[@class='captcha-clk2']") # 等待接下来的元素出现
        
        valid = ocr(drive, "//*[@class='captcha-clk2']", img_path)
        driver.find_element_by_xpath("//*[@placeholder='验证码']").send_keys(valid)

        driver.find_element_by_xpath("//*[@type='submit']").click()
        is_visible(driver, "//*[@class='charge-header clearfix']") # 等待接下来的元素出现

        if driver.find_elements_by_xpath("//*[@class='usercheck checkin']") == []: # 如果已经签到过，就不要签到了
            return

        driver.find_element_by_xpath("//*[@class='usercheck checkin']").click()
        print('gamekegs签到成功')

    finally:
        driver.quit()

if __name__ == '__main__':
    driver = get_web_driver()
    gamekegs(driver)