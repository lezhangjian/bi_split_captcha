from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
from PIL import Image
from io import BytesIO
from selenium.webdriver import ActionChains
import time

# driver = webdriver.Chrome()
# driver.get('https://baidu.com')
# locator = (By.LINK_TEXT, '贴吧')


class Bilibili():
    def __init__(self):
        self.chrome_options = Options()
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser,5)
        self.action = ActionChains(self.browser)

    def input_user_pwd(self):
        url = 'https://passport.bilibili.com/login'
        self.browser.get(url)
        user = self.browser.find_element(By.ID,'login-username')
        pwd = self.browser.find_element(By.ID,'login-passwd')
        user.send_keys('178642321**')
        pwd.send_keys('*****')

    # 获取残缺的验证码图片和完整的验证码图片
    def get_captcha(self):
        # 获取有缺口的验证码图片
        cut_img_list = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, ('//div[@class="gt_cut_bg gt_show"]/div')))
        )
        # 需要讲(用\来取消特殊用途,,只当作字符串
        cut_img_url = re.search(r'url\("(.*?)"',cut_img_list[0].get_attribute('style'))[1]
        cut_position_list = [
            re.search(r'position: -(.*?)px -?(.*?)px;',i.get_attribute('style')).groups(1) for i in cut_img_list
        ]
        cut_img = self.split_img(cut_img_url, cut_position_list)

        full_img_list = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, ('//div[@class="gt_cut_fullbg gt_show"]/div')))
        )
        full_img_url = re.search(r'url\("(.*?)"', full_img_list[0].get_attribute('style'))[1]
        full_position_list = [
            re.search(r'position: -(.*?)px -?(.*?)px;',i.get_attribute('style')).groups(1) for i in full_img_list
        ]
        full_img = self.split_img(full_img_url, full_position_list)
        return (cut_img,full_img)

    # 拼接图片
    def split_img(self ,url ,positions):
        response = requests.get(url)
        #获取图片的二进制流
        img = response.content
        # 打开二进制流的图片  BytesIO(img)将二进制流转化为图片
        img = Image.open(BytesIO(img))
        # 创建一张新的图片,,用于粘贴
        new_img = Image.new('RGB', (260, 116))
        up_img = 0
        low_img = 0
        # 拼接上半部分的图片
        for i in range(26):
            crop_img = img.crop((int(positions[i][0]),58,int(positions[i][0])+10,116))
            new_img.paste(crop_img,(up_img,0))
            up_img += 10
        # 拼接下半部分的图片
        for i in range(26,52):
            crop_img = img.crop((int(positions[i][0]),0,int(positions[i][0])+10,58))
            new_img.paste(crop_img,(low_img,56))
            low_img += 10
        return new_img

    # 算出偏移量
    def get_offset(self,cut_img,full_img):
        for x in range(50,260):
            for y in range(116):
                cut_data = cut_img.getpixel((x,y))
                full_data = full_img.getpixel((x,y))
                for i in range(3):
                    if abs(cut_data[i] - full_data[i]) > 50:
                        return (x,y)

    def move_img(self,xoffset,yoffset):
        button = self.wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="gt_slider_knob gt_show"]')))
        self.action.click_and_hold(button).perform()
        time.sleep(0.3)
        self.action.move_by_offset(xoffset-2,yoffset).release().perform()
        time.sleep(0.3)


if __name__ == '__main__':
    bili = Bilibili()
    bili.input_user_pwd()
    cut_img,full_img = bili.get_captcha()
    x,y = bili.get_offset(cut_img,full_img)
    bili.move_img(x,y)




