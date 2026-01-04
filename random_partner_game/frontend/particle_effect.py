"""
粒子效果类 - 用于匹配动画
"""
try:
    import pygame
    
    class ParticleEffect:
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.particles = []
            # 初始化一些粒子
            import random
            for _ in range(50):
                self.particles.append({
                    'x': width // 2,
                    'y': height // 2,
                    'vx': (random.random() - 0.5) * 4,
                    'vy': (random.random() - 0.5) * 4,
                    'life': 100,
                    'color': (255, 255, 255)
                })
        
        def update(self):
            for particle in self.particles[:]:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 1
                if particle['life'] <= 0:
                    self.particles.remove(particle)
        
        def draw(self, surface):
            for particle in self.particles:
                pygame.draw.circle(
                    surface,
                    particle['color'],
                    (int(particle['x']), int(particle['y'])),
                    3
                )
except ImportError:
    # pygame 不可用时的占位实现
    class ParticleEffect:
        def __init__(self, width, height):
            pass
        def update(self):
            pass
        def draw(self, surface):
            pass

