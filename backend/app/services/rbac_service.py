"""
Role-Based Access Control (RBAC) Service

Handles hierarchical filtering and permission checks for all endpoints.
Implements the organizational hierarchy access rules:

- ADMIN: System-wide access to all data
- HR: Multi-contract access (can see multiple contracts they're assigned to)
- PM: Contract-wide access (sees all departments and users within their contract)
- MANAGER: Department hierarchy access (sees direct and indirect reports)
- BENEFICIARY: Self-only access (only their own data)
"""

from typing import List, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.user import User, UserRole
from app.models.beneficiary import Beneficiary
from app.models.department import Department
from app.models.petition import Petition
from app.models.todo import Todo
from app.models.case_group import CaseGroup


class RBACService:
    """Role-Based Access Control service for hierarchical data filtering."""
    
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
        self._accessible_user_ids = None
        self._accessible_beneficiary_ids = None
        self._accessible_department_ids = None
        
    def get_accessible_user_ids(self) -> Set[str]:
        """
        Get all user IDs that the current user can access based on role hierarchy.
        
        Returns:
            Set of user IDs the current user can access
        """
        if self._accessible_user_ids is not None:
            return self._accessible_user_ids
            
        accessible_ids = set()
        
        if self.current_user.role == UserRole.ADMIN:
            # ADMIN: All users
            all_users = self.db.query(User.id).all()
            accessible_ids = {user_id for user_id, in all_users}
            
        elif self.current_user.role == UserRole.HR:
            # HR: All users in contracts they have access to
            # For now, assume HR can see all users in their contract
            if self.current_user.contract_id:
                contract_users = self.db.query(User.id).filter(
                    User.contract_id == self.current_user.contract_id
                ).all()
                accessible_ids = {user_id for user_id, in contract_users}
            
        elif self.current_user.role == UserRole.PM:
            # PM: All users in their contract
            if self.current_user.contract_id:
                contract_users = self.db.query(User.id).filter(
                    User.contract_id == self.current_user.contract_id
                ).all()
                accessible_ids = {user_id for user_id, in contract_users}
            
        elif self.current_user.role == UserRole.MANAGER:
            # MANAGER: Direct and indirect reports + themselves
            accessible_ids.add(self.current_user.id)
            accessible_ids.update(self._get_all_reports(self.current_user.id))
            
        elif self.current_user.role == UserRole.BENEFICIARY:
            # BENEFICIARY: Only themselves
            accessible_ids.add(self.current_user.id)
            
        self._accessible_user_ids = accessible_ids
        return accessible_ids
    
    def get_accessible_beneficiary_ids(self) -> Set[str]:
        """
        Get all beneficiary IDs that the current user can access.
        
        Returns:
            Set of beneficiary IDs the current user can access
        """
        if self._accessible_beneficiary_ids is not None:
            return self._accessible_beneficiary_ids
            
        accessible_user_ids = self.get_accessible_user_ids()
        
        # Get beneficiaries corresponding to accessible users
        beneficiaries = self.db.query(Beneficiary.id).filter(
            Beneficiary.user_id.in_(accessible_user_ids)
        ).all()
        
        self._accessible_beneficiary_ids = {ben_id for ben_id, in beneficiaries}
        return self._accessible_beneficiary_ids
    
    def get_accessible_department_ids(self) -> Set[str]:
        """
        Get all department IDs that the current user can access.
        
        Returns:
            Set of department IDs the current user can access
        """
        if self._accessible_department_ids is not None:
            return self._accessible_department_ids
            
        accessible_ids = set()
        
        if self.current_user.role in [UserRole.ADMIN]:
            # ADMIN: All departments
            all_depts = self.db.query(Department.id).all()
            accessible_ids = {dept_id for dept_id, in all_depts}
            
        elif self.current_user.role in [UserRole.HR, UserRole.PM]:
            # HR/PM: All departments in their contract
            if self.current_user.contract_id:
                contract_depts = self.db.query(Department.id).filter(
                    Department.contract_id == self.current_user.contract_id
                ).all()
                accessible_ids = {dept_id for dept_id, in contract_depts}
            
        elif self.current_user.role == UserRole.MANAGER:
            # MANAGER: Their department + sub-departments (if any)
            if self.current_user.department_id:
                accessible_ids.add(self.current_user.department_id)
                # TODO: Add sub-department logic if hierarchical departments exist
                
        elif self.current_user.role == UserRole.BENEFICIARY:
            # BENEFICIARY: Their own department only
            if self.current_user.department_id:
                accessible_ids.add(self.current_user.department_id)
                
        self._accessible_department_ids = accessible_ids
        return accessible_ids
    
    def _get_all_reports(self, manager_id: str) -> Set[str]:
        """
        Recursively get all direct and indirect reports for a manager.
        
        Args:
            manager_id: The manager's user ID
            
        Returns:
            Set of user IDs that report to this manager (directly or indirectly)
        """
        reports = set()
        
        # Get direct reports
        direct_reports = self.db.query(User.id).filter(
            User.reports_to_id == manager_id
        ).all()
        
        for report_id, in direct_reports:
            reports.add(report_id)
            # Recursively get their reports
            reports.update(self._get_all_reports(report_id))
            
        return reports
    
    def apply_petition_filters(self, query):
        """
        Apply role-based filters to a Petition query.
        
        Args:
            query: SQLAlchemy query object for Petition
            
        Returns:
            Filtered query object
        """
        if self.current_user.role == UserRole.ADMIN:
            # ADMIN: No filtering, see everything
            return query
            
        elif self.current_user.role in [UserRole.HR, UserRole.PM]:
            # HR/PM: See all applications in their contract
            if self.current_user.contract_id:
                # Filter by beneficiaries in the same contract
                return query.join(Beneficiary).join(User).filter(
                    User.contract_id == self.current_user.contract_id
                )
            else:
                # No contract assigned - see nothing
                return query.filter(False)
                
        elif self.current_user.role == UserRole.MANAGER:
            # MANAGER: See applications for their reports + themselves
            accessible_user_ids = self.get_accessible_user_ids()
            return query.join(Beneficiary).filter(
                Beneficiary.user_id.in_(accessible_user_ids)
            )
            
        elif self.current_user.role == UserRole.BENEFICIARY:
            # BENEFICIARY: Only their own applications
            return query.join(Beneficiary).filter(
                Beneficiary.user_id == self.current_user.id
            )
            
        else:
            # Unknown role - deny access
            return query.filter(False)
    
    def apply_beneficiary_filters(self, query):
        """
        Apply role-based filters to a Beneficiary query.
        
        Args:
            query: SQLAlchemy query object for Beneficiary
            
        Returns:
            Filtered query object
        """
        if self.current_user.role == UserRole.ADMIN:
            # ADMIN: See all beneficiaries
            return query
            
        elif self.current_user.role in [UserRole.HR, UserRole.PM]:
            # HR/PM: See beneficiaries in their contract
            if self.current_user.contract_id:
                return query.join(User).filter(
                    User.contract_id == self.current_user.contract_id
                )
            else:
                return query.filter(False)
                
        elif self.current_user.role == UserRole.MANAGER:
            # MANAGER: See beneficiaries who report to them
            accessible_user_ids = self.get_accessible_user_ids()
            return query.filter(Beneficiary.user_id.in_(accessible_user_ids))
            
        elif self.current_user.role == UserRole.BENEFICIARY:
            # BENEFICIARY: Only themselves
            return query.filter(Beneficiary.user_id == self.current_user.id)
            
        else:
            return query.filter(False)
    
    def apply_todo_filters(self, query):
        """
        Apply role-based filters to a Todo query.
        
        Args:
            query: SQLAlchemy query object for Todo
            
        Returns:
            Filtered query object
        """
        if self.current_user.role == UserRole.ADMIN:
            # ADMIN: See all todos
            return query
            
        elif self.current_user.role in [UserRole.HR, UserRole.PM]:
            # HR/PM: See todos in their contract scope
            accessible_user_ids = self.get_accessible_user_ids()
            return query.filter(
                or_(
                    Todo.assigned_to_user_id.in_(accessible_user_ids),
                    Todo.created_by_user_id.in_(accessible_user_ids)
                )
            )
            
        elif self.current_user.role == UserRole.MANAGER:
            # MANAGER: See todos assigned to or created by their reports + themselves
            accessible_user_ids = self.get_accessible_user_ids()
            return query.filter(
                or_(
                    Todo.assigned_to_user_id.in_(accessible_user_ids),
                    Todo.created_by_user_id.in_(accessible_user_ids)
                )
            )
            
        elif self.current_user.role == UserRole.BENEFICIARY:
            # BENEFICIARY: Only todos assigned to them or they created
            return query.filter(
                or_(
                    Todo.assigned_to_user_id == self.current_user.id,
                    Todo.created_by_user_id == self.current_user.id
                )
            )
            
        else:
            return query.filter(False)
    
    def apply_case_group_filters(self, query):
        """
        Apply role-based filters to a CaseGroup query.
        
        Args:
            query: SQLAlchemy query object for CaseGroup
            
        Returns:
            Filtered query object
        """
        if self.current_user.role == UserRole.ADMIN:
            # ADMIN: See all case groups
            return query
            
        elif self.current_user.role in [UserRole.HR, UserRole.PM]:
            # HR/PM: See case groups for beneficiaries in their contract
            accessible_beneficiary_ids = self.get_accessible_beneficiary_ids()
            return query.filter(CaseGroup.beneficiary_id.in_(accessible_beneficiary_ids))
            
        elif self.current_user.role == UserRole.MANAGER:
            # MANAGER: See case groups for their reports
            accessible_beneficiary_ids = self.get_accessible_beneficiary_ids()
            return query.filter(CaseGroup.beneficiary_id.in_(accessible_beneficiary_ids))
            
        elif self.current_user.role == UserRole.BENEFICIARY:
            # BENEFICIARY: Only their own case groups
            accessible_beneficiary_ids = self.get_accessible_beneficiary_ids()
            return query.filter(CaseGroup.beneficiary_id.in_(accessible_beneficiary_ids))
            
        else:
            return query.filter(False)
    
    def can_access_user(self, user_id: str) -> bool:
        """Check if current user can access a specific user."""
        return user_id in self.get_accessible_user_ids()
    
    def can_access_beneficiary(self, beneficiary_id: str) -> bool:
        """Check if current user can access a specific beneficiary."""
        return beneficiary_id in self.get_accessible_beneficiary_ids()
    
    def can_modify_data(self) -> bool:
        """Check if current user has data modification permissions."""
        return self.current_user.role in [UserRole.ADMIN, UserRole.HR, UserRole.PM, UserRole.MANAGER]
    
    def can_create_users(self) -> bool:
        """Check if current user can create new users."""
        return self.current_user.role in [UserRole.ADMIN, UserRole.HR]
    
    def can_delete_data(self) -> bool:
        """Check if current user can delete data."""
        return self.current_user.role in [UserRole.ADMIN]