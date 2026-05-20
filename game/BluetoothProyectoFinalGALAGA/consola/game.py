import time
import uasyncio as asyncio
from colours import (BLACK, WHITE, CYAN, ORANGE, BLUE, NAVY, YELLOW,
                     PURPLE, LEVEL_COLOURS)
from player import Player
from enemy import Enemy
from bullet import Bullet
from asteroid import Asteroid, Guardian, DiveBomber
from sprites.sprites import (PLAYER_W, PLAYER_H, ALIEN_W, ALIEN_H,
                              FIREBALL_W, FIREBALL_H, GUARDIAN_W, GUARDIAN_H,
                              player_sprite, spawn, spawn1,
                              alien1, alien2, alien3, alien4, alien5, alien6,
                              fireball, fireball1, guardian1, guardian2)

try:
    from urandom import getrandbits, randint
except ImportError:
    from random import getrandbits, randint

WIDTH = 320
HEIGHT = 240
NUM_ROWS = 3
NUM_STARS = 30
ENEMY_DROP = 10

class Game:
    def __init__(self, display, buzzer, btn_fire, btn_pause, ctrl_state):
        self.display = display
        self.buzzer = buzzer
        self.btn_fire = btn_fire
        self.btn_pause = btn_pause
        self.ctrl_state = ctrl_state 

        self.player = Player(WIDTH, HEIGHT)
        self.asteroid = Asteroid(WIDTH, HEIGHT)
        self.guardian = Guardian(WIDTH, HEIGHT)
        self.dive_bomber = DiveBomber(WIDTH, HEIGHT)

        self.enemies = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.stars = []

        self.player_lives = 3
        self.enemy_dir = 1
        self.current_row = 0
        self.last_enemy_move = 0
        self.last_enemy_shot = 0
        self.total_score = 0
        self.level = 1
        self.frame_count = 0

        self.difficulty_mode = 1 
        self.enemy_speed = 10
        self.enemy_rate_of_fire = 60
        self.asteroid_interval = 600
        self.asteroid_speed = 2
        self.dive_bomber_interval = 500
        self.dive_bomber_speed = 2

        self.fire_repeat = 0
        self._prev_lives = 3

    def _count_alive(self):
        c = 0
        for e in self.enemies:
            if e.alive:
                c += 1
        return c

    def _gray565(self, brightness):
        b = brightness >> 3
        g = brightness >> 2
        return (b << 11) | (g << 5) | b

    def _init_stars(self):
        self.stars = []
        for _ in range(NUM_STARS):
            x = randint(0, WIDTH - 1)
            y = randint(0, HEIGHT - 1)
            speed = 1 + (getrandbits(2) % 3)
            base = 8 + (getrandbits(5) % 24)
            self.stars.append([x, y, speed, base, self._gray565(base * 8)])

    def _update_and_draw_stars(self):
        dp = self.display.draw_pixel
        for s in self.stars:
            dp(s[0], s[1], BLACK)
            s[1] += s[2]
            if s[1] >= HEIGHT:
                s[1] = 0
                s[0] = randint(0, WIDTH - 1)
                s[3] = 8 + (getrandbits(5) % 24)
            if getrandbits(6) == 0:
                flicker = (getrandbits(3) % 7) - 3
                b = s[3] + flicker
                if b < 0:
                    b = 0
                if b > 31:
                    b = 31
                s[4] = self._gray565(b * 8)
            dp(s[0], s[1], s[4])

    def _draw_stars(self):
        for s in self.stars:
            self.display.draw_pixel(s[0], s[1], s[4])

    def setup_game(self):
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        for row in range(NUM_ROWS):
            for col in range(8):
                self.enemies.append(Enemy(col * 24 + 10, row * 20 + 40, row))
        self.player = Player(WIDTH, HEIGHT)
        self.player_lives = 3
        self._prev_lives = 3
        self.enemy_dir = 1
        self.current_row = 0
        self.last_enemy_move = 0
        self.last_enemy_shot = 0
        self.total_score = 0
        self.level = 1
        self.frame_count = 0
        self._init_stars()
        self._set_difficulty()

    def _set_difficulty(self):
        lvl = (self.level - 1) % 10
        settings = (
            (60, 600, 2, 500, 2), (50, 400, 3, 480, 3), (40, 300, 4, 460, 4),
            (30, 200, 5, 440, 5), (20, 100, 6, 260, 5), (10, 80,  7, 240, 6),
            (5,  60,  8, 220, 7), (3,  60,  9, 60,  8), (3,  60,  10, 60, 8),
            (3,  60,  11, 60, 9)
        )
        s = settings[lvl]
        
        if self.difficulty_mode == 0:    
            self.enemy_speed = 6
            self.enemy_rate_of_fire = int(s[0] * 1.5)
            self.asteroid_interval = int(s[1] * 1.5)
            self.asteroid_speed = max(1, int(s[2] * 0.6))
            self.dive_bomber_interval = int(s[3] * 1.5)
            self.dive_bomber_speed = max(1, int(s[4] * 0.6))
        elif self.difficulty_mode == 1:  
            self.enemy_speed = 10
            self.enemy_rate_of_fire = s[0]
            self.asteroid_interval = s[1]
            self.asteroid_speed = s[2]
            self.dive_bomber_interval = s[3]
            self.dive_bomber_speed = s[4]
        elif self.difficulty_mode == 2:  
            self.enemy_speed = 15
            self.enemy_rate_of_fire = max(2, int(s[0] * 0.6))
            self.asteroid_interval = max(20, int(s[1] * 0.6))
            self.asteroid_speed = int(s[2] * 1.5)
            self.dive_bomber_interval = max(20, int(s[3] * 0.6))
            self.dive_bomber_speed = int(s[4] * 1.5)

    def _update_bullets(self):
        for b in self.player_bullets:
            b.update()
        for b in self.enemy_bullets:
            b.update()

    def _maybe_enemy_shoot(self):
        alive = self._count_alive()
        if alive == 0:
            return
        if self.frame_count - self.last_enemy_shot < self.enemy_rate_of_fire:
            return
        self.last_enemy_shot = self.frame_count

        alive_list = [e for e in self.enemies if e.alive]
        if not alive_list:
            return
        e = alive_list[randint(0, len(alive_list) - 1)]
        self.enemy_bullets.append(Bullet(e.x + ALIEN_W // 2, e.y + ALIEN_H, 4, ORANGE, HEIGHT))
        self.buzzer.play_enemy_shoot()

    def _move_enemies(self):
        total = len(self.enemies)
        if total == 0:
            return
        alive = self._count_alive()
        delay = alive * 4 // total if total else 1
        if delay < 1:
            delay = 1
        if self.frame_count - self.last_enemy_move < delay:
            return
        self.last_enemy_move = self.frame_count

        can_move = True
        for e in self.enemies:
            if e.alive and e.row == self.current_row:
                if self.enemy_dir > 0:
                    if e.x + ALIEN_W + self.enemy_speed >= WIDTH:
                        can_move = False
                else:
                    if e.x - self.enemy_speed < 0:
                        can_move = False

        if not can_move:
            self.enemy_dir *= -1
            for e in self.enemies:
                if e.alive:
                    e.y += ENEMY_DROP

        for e in self.enemies:
            if e.alive and e.row == self.current_row:
                e.x += self.enemy_dir * self.enemy_speed

        self.current_row += 1
        if self.current_row >= NUM_ROWS:
            self.current_row = 0

    def _collision_detection(self):
        for e in self.enemies:
            for b in self.player_bullets:
                if (b.active and e.alive and
                    b.x >= e.x and b.x <= e.x + ALIEN_W and
                    b.y >= e.y and b.y <= e.y + ALIEN_H):
                    e.alive = False
                    e.explode()
                    self.total_score += e.score
                    self.buzzer.play_explosion()
                    b.active = False

        for b in self.player_bullets:
            if (b.active and self.guardian.active and
                b.x >= self.guardian.x and b.x <= self.guardian.x + GUARDIAN_W and
                b.y >= self.guardian.y and b.y <= self.guardian.y + GUARDIAN_H):
                self.guardian.active = False
                self.guardian.explode()
                self.buzzer.play_explosion()

        for b in self.player_bullets:
            if (b.active and self.dive_bomber.active and
                b.x >= self.dive_bomber.x and b.x <= self.dive_bomber.x + ALIEN_W and
                b.y >= self.dive_bomber.y and b.y <= self.dive_bomber.y + ALIEN_H):
                self.dive_bomber.active = False
                self.dive_bomber.explode()
                self.total_score += 50
                self.buzzer.play_explosion()
                b.active = False

        for e in self.enemies:
            if (self.asteroid.active and e.alive and
                self.asteroid.x >= e.x and self.asteroid.x <= e.x + ALIEN_W and
                self.asteroid.y >= e.y and self.asteroid.y <= e.y + ALIEN_H):
                e.alive = False
                e.explode()
                self.buzzer.play_explosion()

        for b in self.enemy_bullets:
            if (b.active and
                b.x >= self.player.x and b.x <= self.player.x + PLAYER_W and
                b.y >= self.player.y and b.y <= self.player.y + PLAYER_H):
                b.active = False
                self.player_lives -= 1
                self.player.explode()
                self.buzzer.play_killed()

        if (self.asteroid.active and
            self.asteroid.x >= self.player.x and
            self.asteroid.x <= self.player.x + PLAYER_W and
            self.asteroid.y >= self.player.y and
            self.asteroid.y <= self.player.y + PLAYER_H):
            self.asteroid.active = False
            self.player_lives -= 1
            self.player.explode()
            self.buzzer.play_killed()

        if (self.dive_bomber.active and
            self.dive_bomber.x >= self.player.x and
            self.dive_bomber.x <= self.player.x + PLAYER_W and
            self.dive_bomber.y >= self.player.y and
            self.dive_bomber.y <= self.player.y + PLAYER_H):
            self.dive_bomber.active = False
            self.player_lives -= 1
            self.player.explode()
            self.buzzer.play_killed()

        if (self.guardian.active and
            self.guardian.x >= self.player.x and
            self.guardian.x <= self.player.x + PLAYER_W and
            self.guardian.y >= self.player.y and
            self.guardian.y <= self.player.y + PLAYER_H):
            self.guardian.active = False
            if self.player_lives < 3:
                self.player_lives += 1
            self.buzzer.play_powerup()

        for e in self.enemies:
            if (e.alive and
                e.x >= self.player.x - ALIEN_W and
                e.x <= self.player.x + PLAYER_W and
                e.y >= self.player.y - ALIEN_H and
                e.y <= self.player.y + PLAYER_H):
                e.alive = False
                e.explode()
                self.player_lives -= 1
                self.player.explode()
                self.buzzer.play_killed()

    def _render(self):
        fh = self.display.fill_hrect
        fc = self.frame_count

        self._update_and_draw_stars()

        dx = self.player.x - self.player._px
        if dx > 0:
            fh(self.player._px, self.player._py, dx, PLAYER_H, BLACK)
        elif dx < 0:
            fh(self.player.x + PLAYER_W, self.player._py, -dx, PLAYER_H, BLACK)
            
        dy = self.player.y - self.player._py
        if dy > 0:
            fh(self.player._px, self.player._py, PLAYER_W, dy, BLACK)
        elif dy < 0:
            fh(self.player._px, self.player.y + PLAYER_H, PLAYER_W, -dy, BLACK)
            
        self.player.draw(self.display)

        if self.asteroid._pv and (self.asteroid._px != self.asteroid.x or self.asteroid._py != self.asteroid.y or not self.asteroid.active):
            fh(self.asteroid._px, self.asteroid._py, FIREBALL_W, FIREBALL_H, BLACK)
        if self.asteroid.active:
            self.asteroid.draw(self.display, fc)

        if self.guardian._pv and (self.guardian._px != self.guardian.x or self.guardian._py != self.guardian.y or (not self.guardian.active and self.guardian.explode_count == 0)):
            fh(self.guardian._px, self.guardian._py, GUARDIAN_W, GUARDIAN_H, BLACK)
        if self.guardian.active or self.guardian.explode_count > 0:
            self.guardian.draw(self.display, fc)

        if self.dive_bomber._pv and (self.dive_bomber._px != self.dive_bomber.x or self.dive_bomber._py != self.dive_bomber.y or (not self.dive_bomber.active and self.dive_bomber.explode_count == 0)):
            fh(self.dive_bomber._px, self.dive_bomber._py, ALIEN_W, ALIEN_H, BLACK)
        if self.dive_bomber.active or self.dive_bomber.explode_count > 0:
            self.dive_bomber.draw(self.display, fc)

        for e in self.enemies:
            if getattr(e, '_was_visible', False):
                if e._px != e.x or e._py != e.y or (not e.alive and e.explode_count == 0):
                    fh(e._px, e._py, ALIEN_W, ALIEN_H, BLACK)
            
            if e.alive or e.explode_count > 0:
                e.draw(self.display, fc)
                e._was_visible = True
            else:
                e._was_visible = False

        for b in self.player_bullets:
            if hasattr(b, '_px') and (b._px != b.x or b._py != b.y or not b.active):
                fh(b._px, b._py, 2, 4, BLACK)
            b.draw(self.display)
            
        for b in self.enemy_bullets:
            if hasattr(b, '_px') and (b._px != b.x or b._py != b.y or not b.active):
                fh(b._px, b._py, 2, 4, BLACK)
            b.draw(self.display)

        self._update_status()

    def _save_positions(self):
        self.player._px = self.player.x
        self.player._py = self.player.y

        for e in self.enemies:
            e._px = e.x
            e._py = e.y

        for b in self.player_bullets:
            b._px = b.x
            b._py = b.y
        for b in self.enemy_bullets:
            b._px = b.x
            b._py = b.y

        self.asteroid._px = self.asteroid.x
        self.asteroid._py = self.asteroid.y
        self.asteroid._pv = self.asteroid.active

        self.guardian._px = self.guardian.x
        self.guardian._py = self.guardian.y
        self.guardian._pv = self.guardian.active or self.guardian.explode_count > 0

        self.dive_bomber._px = self.dive_bomber.x
        self.dive_bomber._py = self.dive_bomber.y
        self.dive_bomber._pv = self.dive_bomber.active or self.dive_bomber.explode_count > 0

    def _update_status(self):
        score_text = "{:05d} LVL {:2d}".format(self.total_score, self.level)
        color = LEVEL_COLOURS[(self.level - 1) % 10]
        self.display.draw_text8x8(5, 5, score_text, color, BLACK)
        if self.player_lives < self._prev_lives:
            self.display.fill_hrect(WIDTH - 100, 0, 100, 35, BLACK)
        self._prev_lives = self.player_lives
        for idx in range(self.player_lives):
            x_pos = WIDTH - ((idx + 1) * (PLAYER_W + 5))
            self.display.draw_sprite(player_sprite, x_pos, 5, PLAYER_W, PLAYER_H)

    async def _next_level(self):
        self.level += 1
        self._set_difficulty()

        self.display.clear(BLACK)
        self._draw_stars()
        
        lvl_text = "¡NIVEL {}!".format(self.level)
        x_lvl = (WIDTH - len(lvl_text) * 8) // 2
        self.display.draw_text8x8(x_lvl, 110, lvl_text, YELLOW, BLACK)
        
        self.buzzer.play_next_level()
        
        start_transition = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_transition) < 1500:
            self.buzzer.update()
            await asyncio.sleep_ms(10)

        self.display.clear(BLACK)
        self._draw_stars()

        i = 0
        for row in range(NUM_ROWS):
            for col in range(8):
                self.enemies[i].alive = True
                self.enemies[i].x = col * 24 + 10
                self.enemies[i].y = row * 20 + 40
                self.enemies[i].explode_count = 0
                i += 1
                
        self._save_positions()

    def _is_game_over(self):
        for e in self.enemies:
            if e.alive and e.y + ALIEN_H >= HEIGHT:
                return True
        if self.player_lives <= 0:
            return True
        return False

    async def _splash_screen(self):
        self.display.clear(BLACK)
        menu_idx = 0
        while True:
            self.btn_fire.update_state(self.ctrl_state.fire_raw)
            self._update_and_draw_stars()
            
            self.display.draw_text8x8(4, 15, "Universidad Nacional Autonoma de Mexico", YELLOW, BLACK)
            self.display.draw_text8x8(72, 30, "Facultad de Ingenieria", YELLOW, BLACK)
            self.display.draw_text8x8(24, 60, "Proyecto Final - Microcomputadoras", CYAN, BLACK)
            
            self.display.draw_text8x8(132, 90, "Equipo:", ORANGE, BLACK)
            self.display.draw_text8x8(56, 110, "Flores Colin Victor Jaziel", WHITE, BLACK)
            self.display.draw_text8x8(24, 125, "Espinoza Matamoros Percival Ulises", WHITE, BLACK)
            self.display.draw_text8x8(44, 140, "Garcia Cortes Adolfo de jesus", WHITE, BLACK)
            self.display.draw_text8x8(52, 155, "Lara Hernandez Angel Husiel", WHITE, BLACK)
            self.display.draw_text8x8(80, 170, "Lugo Manzano Rodrigo", WHITE, BLACK)
            
            self.display.draw_text8x8(96, 210, "Presiona DISPARO", YELLOW, BLACK)
            
            self.buzzer.play_menu_note(menu_idx)
            menu_idx += 1
            self.buzzer.update()
            
            if self.btn_fire.is_pressed():
                break
            
            await asyncio.sleep_ms(80)

    async def _info_screen(self):
        self.display.clear(BLACK)
        frame = 0
        while True:
            self.btn_fire.update_state(self.ctrl_state.fire_raw)
            self._update_and_draw_stars()
            y = 20
            step = 35
            self.display.draw_sprite(spawn if frame & 0x8 else spawn1, WIDTH // 4, y, 16, 12)
            self.display.draw_text8x8(WIDTH // 2, y, "= 50", LEVEL_COLOURS[0], BLACK)
            y += step
            self.display.draw_sprite(alien1 if frame & 0x8 else alien2, WIDTH // 4, y, 16, 12)
            self.display.draw_text8x8(WIDTH // 2, y, "= 30", LEVEL_COLOURS[1], BLACK)
            y += step
            self.display.draw_sprite(alien3 if frame & 0x8 else alien4, WIDTH // 4, y, 16, 12)
            self.display.draw_text8x8(WIDTH // 2, y, "= 20", LEVEL_COLOURS[2], BLACK)
            y += step
            self.display.draw_sprite(alien5 if frame & 0x8 else alien6, WIDTH // 4, y, 16, 12)
            self.display.draw_text8x8(WIDTH // 2, y, "= 10", LEVEL_COLOURS[3], BLACK)
            y += step
            self.display.draw_sprite(fireball if frame & 0x8 else fireball1, WIDTH // 4, y, 16, 16)
            self.display.draw_text8x8(WIDTH // 2, y, "= ??", LEVEL_COLOURS[4], BLACK)
            y += step
            self.display.draw_sprite(guardian1 if frame & 0x8 else guardian2, WIDTH // 4, y, 16, 16)
            self.display.draw_text8x8(WIDTH // 2, y, "= +1", LEVEL_COLOURS[5], BLACK)
            frame += 1
            self.buzzer.update()
            
            if self.btn_fire.is_pressed():
                break
            await asyncio.sleep_ms(50)

    async def _game_over_screen(self):
        self.display.clear(BLACK)
        self._draw_stars()
        
        txt_game_over = "FIN DEL JUEGO"
        x_game_over = (WIDTH - len(txt_game_over) * 8) // 2
        self.display.draw_text8x8(x_game_over, 80, txt_game_over, WHITE, BLACK)
        
        score_text = "Puntaje: {:05d}".format(self.total_score)
        x_score = (WIDTH - len(score_text) * 8) // 2
        self.display.draw_text8x8(x_score, 120, score_text, CYAN, BLACK)
        
        level_text = "Nivel: {:d}".format(self.level)
        x_level = (WIDTH - len(level_text) * 8) // 2
        self.display.draw_text8x8(x_level, 150, level_text, YELLOW, BLACK)
        
        fire_text = "Presiona DISPARO"
        x_fire = (WIDTH - len(fire_text) * 8) // 2
        self.display.draw_text8x8(x_fire, 200, fire_text, WHITE, BLACK)
        
        while True:
            self.btn_fire.update_state(self.ctrl_state.fire_raw)
            if self.btn_fire.is_pressed():
                break
            self.buzzer.update()
            await asyncio.sleep_ms(50)

    async def _pause(self):
        self.display.fill_hrect(40, 35, 240, 170, BLACK)
        
        options = ["Continuar", "Modo", "Salir al menu"]
        mode_names = ["Facil", "Normal", "Diario"]
        selected = 0
        menu_idx = 0
        last_selected = -1
        last_mode = -1
        last_move_time = 0
        
        self.exit_to_menu = False
        
        while True:
            now = time.ticks_ms()
            self.btn_fire.update_state(self.ctrl_state.fire_raw)
            
            fuerza_x = -self.ctrl_state.x
            
            if time.ticks_diff(now, last_move_time) > 300:
                if fuerza_x > 0.4:
                    selected = (selected + 1) % len(options)
                    last_move_time = now
                elif fuerza_x < -0.4:
                    selected = (selected - 1) % len(options)
                    last_move_time = now

            if selected != last_selected or self.difficulty_mode != last_mode:
                self.display.fill_hrect(40, 35, 240, 170, BLACK)
                self.display.draw_text8x8(140, 50, "PAUSA", CYAN, BLACK)
                
                c_continua = YELLOW if selected == 0 else WHITE
                self.display.draw_text8x8(124, 90, "Continuar", c_continua, BLACK)
                
                diff_text = "Modo: {}".format(mode_names[self.difficulty_mode])
                c_diff = YELLOW if selected == 1 else WHITE
                x_diff = (WIDTH - len(diff_text) * 8) // 2
                self.display.draw_text8x8(x_diff, 120, diff_text, c_diff, BLACK)
                
                c_salir = YELLOW if selected == 2 else WHITE
                self.display.draw_text8x8(108, 150, "Salir al menu", c_salir, BLACK)
                
                last_selected = selected
                last_mode = self.difficulty_mode

            self.buzzer.play_menu_note(menu_idx)
            menu_idx += 1
            self.buzzer.update()

            if self.btn_fire.is_pressed():
                if selected == 0:
                    break
                elif selected == 1:
                    self.difficulty_mode = (self.difficulty_mode + 1) % 3
                    self._set_difficulty()
                elif selected == 2:
                    self.exit_to_menu = True
                    break

            await asyncio.sleep_ms(50)
            
        self.display.fill_hrect(40, 35, 240, 170, BLACK)

    async def run(self):
        while True:
            self.setup_game()
            await self._splash_screen()
            await self._info_screen()
            self.buzzer.play_start()
            self.display.clear(BLACK)
            self._draw_stars()
            self._save_positions()

            while True:
                self.btn_fire.update_state(self.ctrl_state.fire_raw)
                self.btn_pause.update_state(self.ctrl_state.pause_raw)

                if self.btn_pause.is_pressed():
                    await self._pause()

                if getattr(self, 'exit_to_menu', False):
                    break

                self._save_positions()

                fuerza_x = -self.ctrl_state.x
                fuerza_y = -self.ctrl_state.y
                self.player.move_analog(fuerza_x, fuerza_y)

                if self.btn_fire.is_pressed():
                    self.player_bullets.append(
                        Bullet(self.player.x + PLAYER_W // 2,
                               self.player.y, -5, CYAN, HEIGHT))
                    self.buzzer.play_shoot()
                    
                if self.btn_fire.is_held():
                    self.fire_repeat -= 1
                    if self.fire_repeat <= 0:
                        self.player_bullets.append(
                            Bullet(self.player.x + PLAYER_W // 2,
                                   self.player.y, -5, CYAN, HEIGHT))
                        self.buzzer.play_shoot()
                        self.fire_repeat = 3

                self._update_bullets()
                self._collision_detection()
                self._maybe_enemy_shoot()
                self.asteroid.update(self.frame_count, self.asteroid_interval, self.asteroid_speed)
                self.guardian.update(self.frame_count)
                self.dive_bomber.update(self.frame_count, self.dive_bomber_interval,
                                        self.dive_bomber_speed, self.enemies)
                self._move_enemies()

                self._render()

                self.player_bullets = [b for b in self.player_bullets if b.active]
                self.enemy_bullets = [b for b in self.enemy_bullets if b.active]

                self.buzzer.update()
                self.frame_count += 1

                if self._count_alive() == 0:
                    await self._next_level()

                if self._is_game_over():
                    break
                    
                await asyncio.sleep_ms(33)

            if getattr(self, 'exit_to_menu', False):
                self.exit_to_menu = False
                continue

            await self._game_over_screen()