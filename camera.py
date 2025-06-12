class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zoom = 1.0

    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates."""
        screen_x = int((world_x - self.x) * self.zoom + self.screen_width // 2)
        screen_y = int((world_y - self.y) * self.zoom + self.screen_height // 2)
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates."""
        world_x = (screen_x - self.screen_width // 2) / self.zoom + self.x
        world_y = (screen_y - self.screen_height // 2) / self.zoom + self.y
        return world_x, world_y

    def center_on(self, target_x, target_y):
        """Center the camera on a target position."""
        self.x = target_x
        self.y = target_y

    def get_position(self):
        """Get the camera's current position."""
        return self.x, self.y

    def set_position(self, x, y):
        """Set the camera's position."""
        self.x = x
        self.y = y

    def set_zoom(self, zoom):
        """Set the camera zoom level."""
        self.zoom = max(0.1, min(zoom, 10.0)) 