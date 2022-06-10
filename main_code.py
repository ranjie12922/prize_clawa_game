from PIL import Image
import math, pygame, sys, mod
from mod import Hook
from mod import Mine, Time_countdown
from mod import screen
import random

clock = pygame.time.Clock()

# 窗口设置
pygame.init()
pygame.display.set_caption("基于Python的娃娃机游戏--孟紫微")
screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size)
backcolour = (255, 255, 255)
screen.fill(backcolour)
FPS = 60
fclock = pygame.time.Clock()
kind = 0

# 图标初始化
hook = Hook()
man = mod.Matchman(hook.rect.top - 80, hook.rect.left + hook.rect.width / 2 - 50)
# change_img(hook.rect.top-80,hook.rect.left+hook.rect.width/2-50)
news_group = pygame.sprite.Group()
for i in range(3):
    news_group.add(mod.Button(i))
screens = 0
goals = [100, 150, 200, 250, 300, 350]
time_limited = [20, 20, 30, 30, 25, 20]

# 积分
scores = mod.Scores(0)

# clock=pygame.time.Clock()

pygame.mixer.init()
bgm = pygame.mixer.Sound("bgm.wav")
bgm.play()
while 1:
    screen.fill(backcolour)
    if screens == 0:  # 开始界面
        mod.show_back(0)
        for spr in news_group:
            spr.show()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.QUIT
            if event.type == pygame.MOUSEMOTION:
                for spr in news_group:
                    if spr.rect.collidepoint(event.pos):
                        spr.check = 0
                    else:
                        spr.check = 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                for spr in news_group:
                    if spr.rect.collidepoint(event.pos):
                        if spr.index == 0:  # 点击开始按钮
                            level = 0
                            first_draw = 1
                            timee = Time_countdown(time_limited[level])
                            event_count_time = pygame.USEREVENT + 1
                            matchmen_change = pygame.USEREVENT + 2
                            pygame.time.set_timer(event_count_time, 1000)
                            pygame.time.set_timer(matchmen_change, 200)
                            rotate = 1
                            run = 0
                            wait = 0
                            miner_back = 0
                            special_change_speed = 0
                            change_man = True
                            hook.reset()
                            screens = 1
                            finish = 0
                            scores.score = 0
                            kind += 1
                        elif spr.index == 1:
                            screens = 2
                        elif spr.index == 2:
                            sys.exit()
                            pygame.QUIT
    elif screens == 1:  # 游戏主界面

        mod.show_back(1, kind)
        if first_draw:
            timee.reset(time_limited[level])
            kind += 1
            first_draw = 0
            miner_group = mod.set(level, level % 3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.QUIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    run = 1
                    rotate = 0
            if event.type == event_count_time:
                timee.miner()
            if event.type == matchmen_change:
                if run:
                    man.change(level)

        # 碰撞后物体与钩子衔接
        if pygame.sprite.spritecollide(hook, miner_group, False, pygame.sprite.collide_mask):
            miner = pygame.sprite.spritecollide(hook, miner_group, False, pygame.sprite.collide_mask)[0]
            if miner.first:
                miner.first = False
                ayis = (hook.rect.top + hook.rect.height / 2) + (miner.rect.height / 2) * math.sin(
                    math.radians(hook.angle))
                axis = (hook.rect.left + hook.rect.width / 2) - (miner.rect.height / 2) * math.cos(
                    math.radians(hook.angle))
                miner.rect.top = ayis - miner.rect.height / 2
                miner.rect.left = axis - miner.rect.width / 2

                hook.direction = [-hook.direction[0], -hook.direction[1]]
                miner.direction = hook.direction
                if miner.speed >= 1:
                    FPS *= miner.speed
                else:
                    special_change_speed = 1
                    hook.speed = miner.speed
                miner_back = 1
        if rotate:
            if hook.angle == 170:
                hook.turn_direct = -1
            elif hook.angle == 10:
                hook.turn_direct = 1
            hook.rotate(hook.turn_direct)
        if run:
            if hook.rect.left <= 0 or hook.rect.left + hook.rect.width >= screen_size[
                0] or hook.rect.top + hook.rect.height >= screen_size[1]:
                hook.direction = [-hook.direction[0], -hook.direction[1]]
            elif hook.rect.top < hook.ini_top:
                run = 0
                rotate = 1
                hook.reset()
                if miner_back:
                    miner_back = 0
                    scores.score += int(miner.value)
                    miner_group.remove(miner)
                    FPS = 60
                    special_change_speed = 0
                    continue
            elif miner_back and special_change_speed:
                if (-hook.rect.left + hook.ini_left) != 0:
                    r = math.atan((hook.rect.top - hook.ini_top) / (-hook.rect.left + hook.ini_left))
                    hook.direction = [10 * math.cos(r), -10 * math.sin(r)]
                    if (r < 0):
                        hook.direction = [-hook.direction[0], -hook.direction[1]]
            hook.move()
            pygame.draw.line(screen, (0, 0, 0),
                             (hook.rect.left + hook.rect.width / 2, hook.rect.top + hook.rect.height / 2),
                             (hook.ini_left + hook.rect.width / 2, hook.ini_top + hook.rect.height / 2), 4)
        if miner_back:
            miner.direction = hook.direction
            miner.move(hook.speed)
            miner.rect = screen.blit(miner.img, miner.rect)
        for i in miner_group:
            if i.index != 4:
                break
        else:
            finish = 1
        if len(miner_group) == 0 or timee.now == 0 or finish:
            if scores.score >= goals[level] and level <= 5:
                level += 1
                screens = 4
                if level == 6:
                    continue
            else:
                screens = 3
                timee.reset(time_limited[0])
            finish = 0
        for spr in miner_group:
            spr.rect = screen.blit(spr.img, spr.rect)
        mod.show_txt(str(goals[level]), screen_size[0] / 19 * 14, screen_size[1] / 15)
        timee.show()
        man.show()
        scores.show()
        hook.show()
        # hook.rect = screen.blit(hook.load, hook.rect)
        man.show()

    elif screens == 2:  # 规则界面
        mod.show_back(2)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                screens = 0
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.QUIT
    elif screens == 3:  # 失败界面
        mod.show_back(3)
        for event in pygame.event.get():
            if event.type == (pygame.MOUSEBUTTONDOWN or pygame.KEYDOWN):
                screens = 0
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.QUIT
    if screens == 4:  # 成功界面
        mod.show_back(4)
        man.change_img(hook.rect.top - 80, hook.rect.left + hook.rect.width / 2 - 50, level)
        for event in pygame.event.get():
            if event.type == (pygame.MOUSEBUTTONDOWN or pygame.KEYDOWN):
                if level >= 6:
                    screens = 0
                else:
                    screens = 1
                    first_draw = 1
                    hook.reset()
                scores.score = 0

            if event.type == pygame.QUIT:
                sys.exit()
                pygame.QUIT
    pygame.display.update()
    fclock.tick(FPS)
bgm.stop()
