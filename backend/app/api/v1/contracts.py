from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.contract import Contract
from app.schemas.contract import Contract as ContractSchema, ContractCreate, ContractUpdate

router = APIRouter()


@router.get("/", response_model=List[ContractSchema])
async def list_contracts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all contracts."""
    # TODO: Filter by user permissions (HR sees assigned contracts, admin sees all)
    contracts = db.query(Contract).offset(skip).limit(limit).all()
    return contracts


@router.get("/{contract_id}", response_model=ContractSchema)
async def get_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get contract by ID."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return contract


@router.post("/", response_model=ContractSchema, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_in: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new contract (admin only)."""
    # TODO: Check if current_user is admin
    
    # Check if code already exists
    existing = db.query(Contract).filter(Contract.code == contract_in.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract code already exists"
        )
    
    contract = Contract(**contract_in.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    
    return contract


@router.patch("/{contract_id}", response_model=ContractSchema)
async def update_contract(
    contract_id: str,
    contract_update: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update contract information."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # TODO: Check if current_user is admin
    
    update_data = contract_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)
    
    db.commit()
    db.refresh(contract)
    
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a contract (admin only)."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # TODO: Check if current_user is admin
    
    # Check if contract has associated users
    from app.models.user import User as UserModel
    users_count = db.query(UserModel).filter(UserModel.contract_id == contract_id).count()
    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete contract with {users_count} associated users. Please reassign or remove users first."
        )
    
    db.delete(contract)
    db.commit()
    
    return None
