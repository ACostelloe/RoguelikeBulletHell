"""
UI management system.
"""
from typing import Dict, List, Tuple, Optional, Any, Set, Callable
from dataclasses import dataclass, field
import pygame
from entities import Entity, EntityType, Component
from logger import logger
import traceback
import pygame.font

@dataclass
class UIComponent(Component):
    """Component for handling UI elements."""
    element_id: str = ""
    element_type: str = "panel"
    position: Tuple[float, float] = (0, 0)
    size: Tuple[float, float] = (100, 100)
    visible: bool = True
    enabled: bool = True
    layer: int = 0
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    style: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    callbacks: Dict[str, Callable] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "position": self.position,
            "size": self.size,
            "visible": self.visible,
            "enabled": self.enabled,
            "layer": self.layer,
            "parent": self.parent,
            "children": self.children,
            "style": self.style,
            "data": self.data
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIComponent':
        """Create component from dictionary."""
        return cls(
            element_id=data["element_id"],
            element_type=data["element_type"],
            position=tuple(data["position"]),
            size=tuple(data["size"]),
            visible=data["visible"],
            enabled=data["enabled"],
            layer=data["layer"],
            parent=data["parent"],
            children=data["children"],
            style=data["style"],
            data=data["data"]
        )

class UIManager:
    """Manages UI elements and their interactions."""
    
    def __init__(self, entity_manager):
        """Initialize the UI manager."""
        self.entity_manager = entity_manager
        self.elements: Dict[str, Entity] = {}
        self.active_panel: Optional[Entity] = None
        self.focused_element: Optional[str] = None
        self.hovered_element: Optional[str] = None
        self.dragging_element: Optional[Entity] = None
        self.drag_start: Optional[Tuple[int, int]] = None
        self.dragged_element: Optional[str] = None
        self.drag_start_pos: Optional[Tuple[int, int]] = None
        self.last_click_time: float = 0
        self.double_click_interval: float = 0.3  # seconds
        self.last_click_pos: Optional[Tuple[int, int]] = None
        self.double_click_distance: int = 5  # pixels
        pygame.font.init()
        self.default_font = pygame.font.SysFont("Arial", 18)
        
    def create_element(self, element_id: str, element_type: str, 
                      position: Tuple[int, int], size: Tuple[int, int],
                      parent: Optional[str] = None, style: Optional[Dict] = None) -> Entity:
        """Create a new UI element."""
        # Create entity with UI component
        entity = self.entity_manager.create_entity(EntityType.UI, element_id)
        ui_component = UIComponent(entity)
        entity.add_component(ui_component)
        
        # Configure UI component
        ui_component.element_id = element_id
        ui_component.element_type = element_type
        ui_component.position = position
        ui_component.size = size
        ui_component.parent = parent
        ui_component.style = style or {}
        ui_component.style.setdefault("font", self.default_font)
        
        # Add to elements dictionary
        self.elements[element_id] = entity
        
        # Handle parent-child relationship
        if parent and parent in self.elements:
            parent_entity = self.elements[parent]
            if parent_entity.has_component(UIComponent):
                parent_component = parent_entity.get_component(UIComponent)
                parent_component.children.append(element_id)
                
        return entity
            
    def delete_element(self, element_id: str) -> None:
        """Delete a UI element."""
        try:
            if element_id not in self.elements:
                return
                
            # Remove from parent
            entity = self.elements[element_id]
            ui = entity.get_component(UIComponent)
            if ui and ui.parent and ui.parent in self.elements:
                parent_entity = self.elements[ui.parent]
                parent_ui = parent_entity.get_component(UIComponent)
                if parent_ui and element_id in parent_ui.children:
                    parent_ui.children.remove(element_id)
                    
            # Remove children
            for child_id in ui.children[:]:
                self.delete_element(child_id)
                
            # Remove element
            del self.elements[element_id]
            
        except Exception as e:
            logger.error(f"Error deleting UI element: {str(e)}")
            logger.error(traceback.format_exc())
            
    def get_element(self, element_id: str) -> Optional[Entity]:
        """Get a UI element by ID."""
        return self.elements.get(element_id)
        
    def get_element_at(self, position: Tuple[float, float]) -> Optional[Entity]:
        """Get the UI element at a position."""
        try:
            # Check elements in reverse layer order
            for element_id in sorted(self.elements.keys(),
                                  key=lambda x: self.elements[x].get_component(UIComponent).layer,
                                  reverse=True):
                entity = self.elements[element_id]
                ui = entity.get_component(UIComponent)
                # Skip invisible or disabled elements
                if not ui.visible or not ui.enabled:
                    continue
                    
                # Get element rect
                rect = pygame.Rect(ui.position[0], ui.position[1],
                                 ui.size[0], ui.size[1])
                                 
                # Check if position is inside
                if rect.collidepoint(position):
                    return entity
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting element at position: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    def has_focus(self) -> bool:
        """Check if any UI element currently has focus."""
        if not self.active_panel:
            return False
            
        ui = self.active_panel.get_component(UIComponent)
        return ui is not None and ui.visible

    def set_active_panel(self, panel: Optional[Entity]) -> None:
        """Set the currently active panel."""
        if panel and not panel.has_component('UI'):
            logger.warning("Attempting to set non-UI entity as active panel")
            return
        self.active_panel = panel
        if panel:
            panel.get_component('UI').on_focus()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""
        # If no active panel, UI doesn't have focus
        if not self.has_focus():
            return False

        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if click is within active panel
                if self.active_panel:
                    ui = self.active_panel.get_component('UI')
                    if ui and ui.is_visible() and ui.rect.collidepoint(event.pos):
                        self.focused_element = self.active_panel
                        return True
                return False
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    if self.focused_element:
                        ui = self.focused_element.get_component(UIComponent)
                        if ui and "release" in ui.callbacks:
                            ui.callbacks["release"](event)
                            return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.focused_element:
                        ui = self.focused_element.get_component(UIComponent)
                        if ui and "click" in ui.callbacks:
                            ui.callbacks["click"](event)
                            return True
            return False
        except Exception as e:
            logger.error(f"Error handling event: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    def update(self, dt: float) -> None:
        """Update UI elements."""
        try:
            for element_id, entity in self.elements.items():
                ui = entity.get_component(UIComponent)
                if not ui or not ui.visible:
                    continue
                    
                # Call update callback
                if "update" in ui.callbacks:
                    ui.callbacks["update"](dt)
                    
        except Exception as e:
            logger.error(f"Error updating UI: {str(e)}")
            logger.error(traceback.format_exc())
            
    def _render_element(self, entity, surface):
        ui = entity.get_component(UIComponent)
        if not ui or not ui.visible:
            return
        rect = pygame.Rect(ui.position[0], ui.position[1], ui.size[0], ui.size[1])
        # Draw element background
        if "background_color" in ui.style:
            pygame.draw.rect(surface, ui.style["background_color"], rect)
        # Draw element border
        if "border_color" in ui.style and "border_width" in ui.style:
            pygame.draw.rect(surface, ui.style["border_color"], rect, ui.style["border_width"])
        # Draw element text
        text = ui.data.get("text")
        if text and "font" in ui.style and "font_color" in ui.style:
            font = ui.style["font"]
            font_color = ui.style["font_color"]
            text_surf = font.render(text, True, font_color)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)
        # Call render callback
        if "render" in ui.callbacks:
            ui.callbacks["render"](surface, rect)
        # Recursively render children
        for child_id in ui.children:
            child_entity = self.elements.get(child_id)
            if child_entity:
                self._render_element(child_entity, surface)

    def render(self, surface: pygame.Surface) -> None:
        """Render UI elements recursively."""
        try:
            # Render only top-level elements (no parent)
            top_level = [e for e in self.elements.values() 
                        if e.has_component(UIComponent) and 
                        not e.get_component(UIComponent).parent]
            for entity in sorted(top_level, key=lambda x: x.get_component(UIComponent).layer):
                self._render_element(entity, surface)
        except Exception as e:
            logger.error(f"Error rendering UI: {str(e)}")
            logger.error(traceback.format_exc())
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary."""
        return {
            "elements": {
                element_id: entity.get_component(UIComponent).to_dict()
                for element_id, entity in self.elements.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIManager':
        """Create manager from dictionary."""
        manager = cls()
        for element_id, element_data in data["elements"].items():
            entity = Entity(EntityType.EFFECT)
            ui = UIComponent.from_dict(element_data)
            entity.add_component(ui)
            manager.elements[element_id] = entity
        return manager

    def set_element_text(self, element_id: str, text: str) -> None:
        """Set the text of a UI element by ID."""
        element = self.get_element(element_id)
        if element:
            ui = element.get_component(UIComponent)
            if ui:
                ui.data['text'] = text

    def set_element_callback(self, element_id: str, callback: callable, event_type: str = "click") -> None:
        """Set a callback for a UI element by ID. Default event_type is 'click'."""
        element = self.get_element(element_id)
        if element:
            ui = element.get_component(UIComponent)
            if ui:
                ui.callbacks[event_type] = callback 

    def is_point_inside_panel(self, point: Tuple[int, int]) -> bool:
        """Check if a point is inside any visible panel."""
        if not self.active_panel:
            return False
            
        ui = self.active_panel.get_component(UIComponent)
        if not ui or not ui.visible:
            return False
            
        rect = pygame.Rect(ui.position[0], ui.position[1], ui.size[0], ui.size[1])
        return rect.collidepoint(point) 