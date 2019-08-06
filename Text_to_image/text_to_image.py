from PIL import Image, ImageFont, ImageDraw
import pygame


def text_to_img(text):
    i = Image.new('RGB', (705, 300), (255, 255, 255))
    d = ImageDraw.Draw(i)
    f = ImageFont.truetype(r'C:\Windows\Fonts\SourceHanSansSC-Medium.otf', 58)

    # ascent, descent = f.getmetrics()
    # print(ascent, descent)
    # (width, baseline), (offset_x, offset_y) = f.font.getsize(text)
    # print(width, baseline, offset_x, offset_y)
    # left, top, right, bottom = f.getmask(text).getbbox()
    # print(left, top, right, bottom)
    # d.rectangle((left, top, right, bottom), (0, 0, 0))

    d.text((125, 35), text, font=f, fill='#000000')
    # , spacing=40
    # if there is no blank line, change line spacing by above parameter
    i.save('text_to_img_by_pil.png')


def text_to_img_2(text):
    pygame.init()
    display_surface = pygame.display.set_mode((705, 300))
    display_surface.fill((255, 255, 255))
    t1, t2 = text.split(' ')
    f1 = pygame.font.Font(r'C:\Windows\Fonts\SourceHanSansSC-Medium.otf', 58)
    ft1 = f1.render(t1, True, (0, 0, 0), (255, 255, 255))
    ft1_pos = ft1.get_rect()
    ft1_pos.center = (352, 100)

    f2 = pygame.font.Font(r'C:\Windows\Fonts\SourceHanSansSC-Medium.otf', 58)
    ft2 = f2.render(t2, True, (0, 0, 0), (255, 255, 255))
    ft2_pos = ft2.get_rect()
    ft2_pos.center = (352, 200)

    display_surface.blit(ft1, ft1_pos)
    display_surface.blit(ft2, ft2_pos)

    pygame.display.flip()
    pygame.image.save(display_surface, 'text_to_img_by_pygame.png')


if __name__ == '__main__':
    t = '甄士隐梦幻识通灵 贾雨村风尘怀闺秀'
    # t = u'sky is blue'
    text_to_img(t.replace(' ', '\n\n'))
    text_to_img_2(t)
