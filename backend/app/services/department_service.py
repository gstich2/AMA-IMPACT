"""
Department service for hierarchical operations
"""
from typing import List
from sqlalchemy.orm import Session

from app.models.department import Department


def get_department_hierarchy(db: Session, department_id: str) -> List[str]:
    """
    Get department ID and all its child department IDs recursively.
    
    Args:
        db: Database session
        department_id: Root department ID
        
    Returns:
        List of department IDs including the root and all descendants
    """
    department_ids = [department_id]
    
    # Recursive function to get all children
    def get_children(parent_id: str):
        children = db.query(Department).filter(
            Department.parent_department_id == parent_id,
            Department.is_active == True
        ).all()
        
        for child in children:
            department_ids.append(child.id)
            get_children(child.id)  # Recursive call for grandchildren
    
    get_children(department_id)
    return department_ids


def get_department_tree(db: Session, contract_id: str = None) -> List[dict]:
    """
    Get departments organized as a tree structure.
    
    Args:
        db: Database session
        contract_id: Optional contract filter
        
    Returns:
        List of department dictionaries with nested children
    """
    query = db.query(Department).filter(Department.is_active == True)
    if contract_id:
        query = query.filter(Department.contract_id == contract_id)
    
    departments = query.all()
    
    # Build lookup dict
    dept_dict = {dept.id: {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "parent_id": dept.parent_department_id,
        "children": []
    } for dept in departments}
    
    # Build tree
    roots = []
    for dept in departments:
        if dept.parent_department_id is None:
            roots.append(dept_dict[dept.id])
        else:
            parent = dept_dict.get(dept.parent_department_id)
            if parent:
                parent["children"].append(dept_dict[dept.id])
    
    return roots