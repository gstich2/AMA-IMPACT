"""
Department/Organizational Unit Model
Supports flexible tree structure for organizational hierarchy
"""
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Department(Base):
    """
    Organizational unit with self-referencing tree structure.
    Supports unlimited depth and flexible hierarchy.
    
    Examples:
    - Contract → Code → SubCode (3 levels)
    - Contract → SubCode (2 levels, skipping Code)
    - Contract → Code → SubCode → Team (4 levels)
    
    Structure:
    ASSESS (Contract)
    ├── TNA (Department, level=1)
    ├── AV (Department, level=1)  
    └── TS (Department, level=1)
        ├── TSM (Department, level=2, parent=TS)
        └── TSA (Department, level=2, parent=TS)
    
    Or flat structure:
    ASSESS (Contract)
    ├── TNA (Department, level=1, parent=null)
    ├── TSM (Department, level=1, parent=null)
    └── TSA (Department, level=1, parent=null)
    """
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Department info
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, index=True)  # TNA, TS, TSM, etc.
    description = Column(Text, nullable=True)
    
    # Hierarchy
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=False, index=True)
    parent_id = Column(String(36), ForeignKey("departments.id"), nullable=True, index=True)
    level = Column(Integer, nullable=False, default=1)  # 1=top level under contract, 2=sub-level, etc.
    
    # Manager/Lead for this department
    manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="departments")
    
    # Self-referencing for tree structure
    parent = relationship("Department", remote_side=[id], back_populates="children", foreign_keys=[parent_id])
    children = relationship("Department", back_populates="parent", foreign_keys=[parent_id], cascade="all, delete-orphan")
    
    # Users in this department
    users = relationship("User", back_populates="department", foreign_keys="User.department_id")
    
    # Manager of this department
    manager = relationship("User", foreign_keys=[manager_id], post_update=True)
    
    def __repr__(self):
        return f"<Department {self.code} - {self.name}>"
    
    def get_full_path(self):
        """Get full hierarchical path (e.g., 'ASSESS > TS > TSM')"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.code}"
        return f"{self.contract.code} > {self.code}"
    
    def get_all_descendants(self):
        """Recursively get all departments under this one"""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def get_all_users_in_tree(self):
        """Get all users in this department and all sub-departments"""
        users = list(self.users)
        for child in self.children:
            users.extend(child.get_all_users_in_tree())
        return users
