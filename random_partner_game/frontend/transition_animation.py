"""
过渡动画类 - 用于匹配成功后的穿越动画
"""
try:
    import pygame
    
    class TransitionAnimation:
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.running = False
            self.frame = 0
            self.max_frames = 60  # 1秒动画（60fps）
        
        def start(self):
            self.running = True
            self.frame = 0
        
        def update(self):
            if not self.running:
                return False
            self.frame += 1
            if self.frame >= self.max_frames:
                self.running = False
                return False
            return True
        
        def draw(self, surface):
            if not self.running:
                return
            # 简单的淡入淡出效果
            alpha = int(255 * (1 - self.frame / self.max_frames))
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(alpha)
            overlay.fill((255, 255, 255))
            surface.blit(overlay, (0, 0))
except ImportError:
    # pygame 不可用时的占位实现
    class TransitionAnimation:
        def __init__(self, width, height):
            self.running = False
        def start(self):
            self.running = True
        def update(self):
            return False
        def draw(self, surface):
            pass

