"""
Dummy UI Manager for testing purposes.
"""
from typing import Optional, Any, Tuple, Dict

class DummyComponent:
    def __init__(self):
        self.data = {}

class DummyElement:
    def __init__(self, props):
        self.__dict__.update(props)
    def get_component(self, component_type):
        return DummyComponent()

class DummyUIManager:
    """A dummy UI manager for testing purposes."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the dummy UI manager."""
        self.focused_element = None
        self.elements = {}
        self.visible = True
        
    def add_element(self, element_id: str, element: Any) -> None:
        """Add a UI element."""
        self.elements[element_id] = element
        
    def remove_element(self, element_id: str) -> None:
        """Remove a UI element."""
        if element_id in self.elements:
            del self.elements[element_id]
            
    def get_element(self, element_id: str) -> Optional[Any]:
        """Get a UI element by ID."""
        return self.elements.get(element_id)
        
    def set_focus(self, element_id: Optional[str]) -> None:
        """Set the focused element."""
        self.focused_element = element_id
        
    def get_focus(self) -> Optional[str]:
        """Get the currently focused element."""
        return self.focused_element
        
    def show(self) -> None:
        """Show the UI."""
        self.visible = True
        
    def hide(self) -> None:
        """Hide the UI."""
        self.visible = False
        
    def is_visible(self) -> bool:
        """Check if the UI is visible."""
        return self.visible
        
    def update(self) -> None:
        """Update the UI state."""
        pass
        
    def render(self, surface) -> None:
        """Render the UI."""
        pass

    def create_element(self, element_id: str, element_type: str, position: Tuple[int, int], 
                      size: Tuple[int, int], style: Optional[Dict[str, Any]] = None, parent: Any = None, **kwargs) -> Any:
        """Create a UI element.
        
        Args:
            element_id: Unique identifier for the element
            element_type: Type of element to create (e.g., 'panel', 'button')
            position: (x, y) position of the element
            size: (width, height) size of the element
            style: Optional style dictionary for the element
            parent: Optional parent element
            kwargs: Any additional keyword arguments
        Returns:
            The created element
        """
        # Create a dummy element with the given properties
        element = {
            'id': element_id,
            'type': element_type,
            'position': position,
            'size': size,
            'style': style or {},
            'parent': parent,
            'visible': True
        }
        # Store the element
        self.elements[element_id] = element
        # Return a dummy element object with get_component
        return DummyElement(element)

    def set_element_text(self, element_id: str, text: str) -> None:
        """Set the text of a UI element (stub for testing)."""
        pass 

    def set_element_callback(self, element_id: str, callback) -> None:
        """Set the callback for a UI element (stub for testing)."""
        pass 