from typing import Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.session import get_session

router = APIRouter()


@router.get("/all")
async def profile_listing(params: Dict[str, str], db: Session = Depends(get_session)):
    pass


@router.get("/analysis")
async def all_profile_analysis(params: Dict[str, str], db: Session = Depends(get_session)):
    pass


@router.get("/analysis/{profile_id}")
async def get_profile_analysis(params: Dict[str, str], db: Session = Depends(get_session)):
    pass
