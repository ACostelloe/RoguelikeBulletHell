import pygame
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a simple rectangle sprite
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 255, 0))  # Green color
        self.rect = self.image.get_rect(center=(x, y))
        
        # Movement properties
        self.vel_x = 0
        self.vel_y = 0
        self.move_speed = 5
        self.jump_power = -20
        self.gravity = 0.5
        self.on_ground = False
        self.facing_right = True
        self.max_fall_speed = 15
        
        # Combat properties
        self.health = 100
        self.max_health = 100
        self.bullet_damage = 10
        self.shoot_cooldown = 0
        self.shoot_delay = 20
        self.invincible = False
        self.invincibility_timer = 0
        
        # Grappling hook properties
        self.hook_active = False
        self.hook_x = 0
        self.hook_y = 0
        self.hook_speed = 10
        self.hook_range = 300
        self.hook_cooldown = 0
        self.hook_delay = 0
        
        # Stats
        self.stats = {
            'max_health': 100,
            'move_speed': 5,
            'jump_power': 20,
            'bullet_damage': 10,
            'hook_range': 300
        }

    def _activate_grapple(self, target_pos):
        """Activate the grappling hook towards the target position."""
        print(f"[DEBUG] _activate_grapple called, hook_active: {self.hook_active}, hook_cooldown: {self.hook_cooldown}")
        if not self.hook_active:
            # Calculate direction
            dx = target_pos[0] - self.rect.centerx
            dy = target_pos[1] - self.rect.centery
            length = math.sqrt(dx * dx + dy * dy)
            print(f"[DEBUG] Grapple target: {target_pos}, player: ({self.rect.centerx}, {self.rect.centery}), length: {length}")
            # Check if target is within range
            if length <= self.hook_range:
                self.hook_active = True
                self.hook_x = target_pos[0]
                self.hook_y = target_pos[1]
                self.hook_cooldown = self.hook_delay
                print(f"[DEBUG] Grapple activated! hook_x: {self.hook_x}, hook_y: {self.hook_y}")

    def update(self, mouse_pos, platforms, bullet_manager, screen_width, screen_height):
        """Update player state."""
        # Handle movement input
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        print(f"[DEBUG] mouse_buttons: {mouse_buttons}, hook_active: {self.hook_active}")
        
        # Only reset velocity if not grappling
        if not self.hook_active:
            self.vel_x = 0
        
        # Track if any movement is happening
        is_moving = False
        
        # Horizontal movement
        if not self.hook_active:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vel_x = -self.move_speed
                self.facing_right = False
                is_moving = True
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vel_x = self.move_speed
                self.facing_right = True
                is_moving = True
        
        # Jump
        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground and not self.hook_active:
            self.vel_y = self.jump_power
            self.on_ground = False
        
        # Apply gravity (reduced while grappling for a stronger pull)
        if not self.hook_active:
            self.vel_y += self.gravity
        else:
            self.vel_y += self.gravity * 0.2  # Less gravity while grappling
        
        # Limit fall speed
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
        
        # Store old position for collision resolution
        old_rect = self.rect.copy()
        
        # Update hook position (before moving)
        self._update_hook()
        
        # Update position
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        
        # Keep player in bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.vel_y = 0
            self.on_ground = True
        
        # Check platform collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Calculate overlap
                dx = min(self.rect.right - platform.rect.left, platform.rect.right - self.rect.left)
                dy = min(self.rect.bottom - platform.rect.top, platform.rect.bottom - self.rect.top)
                
                # Resolve collision based on smallest overlap
                if dx < dy:
                    # Horizontal collision
                    if self.rect.centerx < platform.rect.centerx:
                        self.rect.right = platform.rect.left
                    else:
                        self.rect.left = platform.rect.right
                    self.vel_x = 0
                else:
                    # Vertical collision
                    if self.rect.centery < platform.rect.centery:
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        if self.hook_active:
                            self.hook_active = False  # Stop grappling if landed
                    else:
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0
                        if self.hook_active:
                            self.hook_active = False
        
        # Handle shooting
        if mouse_buttons[0] and not self.hook_active:  # Left mouse button
            self._shoot(mouse_pos, bullet_manager)
        
        # Handle grappling hook
        if mouse_buttons[2]:  # Right mouse button
            print("[DEBUG] Right mouse button detected, calling _activate_grapple")
            self._activate_grapple(mouse_pos)
        
        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

    def _shoot(self, target_pos, bullet_manager):
        """Shoot a bullet towards the target position."""
        if self.shoot_cooldown <= 0:
            start_pos = (self.rect.centerx, self.rect.centery)
            speed = 10
            damage = self.bullet_damage
            size = 8
            color = (0, 255, 255)
            bullet_manager.create_bullet(
                start_pos,
                target_pos,
                speed,
                damage,
                True,
                size,
                color
            )
            self.shoot_cooldown = self.shoot_delay

    def _update_hook(self):
        """Update hook position and movement."""
        if not self.hook_active:
            return
        
        # Calculate direction to hook point
        dx = self.hook_x - self.rect.centerx
        dy = self.hook_y - self.rect.centery
        length = math.sqrt(dx * dx + dy * dy)
        
        hook_speed = self.hook_speed * 2  # Stronger pull
        if length > 0:
            # Normalize direction
            dx /= length
            dy /= length
            
            # Move towards hook point
            self.vel_x = dx * hook_speed
            self.vel_y = dy * hook_speed
            
            # Snap to hook point if close
            if length < 20:
                self.rect.centerx = int(self.hook_x)
                self.rect.centery = int(self.hook_y)
                self.hook_active = False
                self.vel_x = 0
                self.vel_y = 0

    def take_damage(self, amount):
        """Take damage if not invincible."""
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincibility_timer = 60  # 1 second of invincibility at 60 FPS
            
            # Ensure health doesn't go below 0
            if self.health < 0:
                self.health = 0

    def is_dead(self):
        """Check if the player is dead."""
        return self.health <= 0

    def draw(self, screen):
        """Draw the player."""
        screen.blit(self.image, self.rect)
        
        # Draw hook line and target if active
        if self.hook_active:
            pygame.draw.line(screen, (255, 255, 255),
                            (self.rect.centerx, self.rect.centery),
                            (self.hook_x, self.hook_y), 2)
            pygame.draw.circle(screen, (0, 255, 255), (int(self.hook_x), int(self.hook_y)), 8, 2)
        
        # Draw debug info
        font = pygame.font.Font(None, 20)
        debug_info = [
            f"Position: ({self.rect.x}, {self.rect.y})",
            f"Velocity: ({self.vel_x:.1f}, {self.vel_y:.1f})",
            f"On Ground: {self.on_ground}",
            f"Health: {self.health}/{self.max_health}",
            f"Hook: {self.hook_active}"
        ]
        
        for i, text in enumerate(debug_info):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 40 + i * 20)) 