import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload

from app.models.users import User, UserProfile
from app.models.institutions import Student, Institution
from app.models.skills import Skill
from app.models.community import CommunityPost, CommunityComment, PeerSkillRequest, Activity
from app.models.notifications import Notification

from app.schemas.community import (
    AuthorInfo,
    CommunityPostCreate,
    CommunityPostUpdate,
    CommunityPostRead,
    CommunityCommentCreate,
    CommunityCommentUpdate,
    CommunityCommentRead,
    PeerSkillRequestCreate,
    PeerSkillRequestUpdate,
    PeerSkillRequestRead,
    ActivityRead,
)


class CommunityService:

    @staticmethod
    def _build_author_info(user: User) -> AuthorInfo:
        user_prof = user.profile if hasattr(user, 'profile') and user.profile else None
        name = f"{user_prof.first_name} {user_prof.last_name}".strip() if user_prof and user_prof.first_name else user.username
        avatar_url = user_prof.avatar_url if user_prof else None
        return AuthorInfo(
            user_id=user.id,
            name=name,
            avatar_url=avatar_url,
            role=user.role
        )

    @classmethod
    async def get_posts(
        cls,
        db: AsyncSession,
        user: User,
        post_type: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[CommunityPostRead]:
        stmt = (
            select(CommunityPost)
            .options(
                joinedload(CommunityPost.author_user).joinedload(User.profile),
                selectinload(CommunityPost.comments).joinedload(CommunityComment.author_user).joinedload(User.profile),
            )
        )

        if post_type:
            stmt = stmt.where(CommunityPost.post_type == post_type.upper().strip())

        if search:
            search_pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    CommunityPost.title.ilike(search_pattern),
                    CommunityPost.content.ilike(search_pattern),
                )
            )

        stmt = stmt.order_by(desc(CommunityPost.created_at))
        res = await db.execute(stmt)
        posts = res.scalars().unique().all()

        results = []
        for post in posts:
            author_dto = cls._build_author_info(post.author_user)
            results.append(
                CommunityPostRead(
                    id=post.id,
                    author=author_dto,
                    title=post.title,
                    content=post.content,
                    post_type=post.post_type,
                    tags=post.tags,
                    upvotes_count=post.upvotes_count,
                    created_at=post.created_at,
                    comments_count=len(post.comments or []),
                    comments=[]
                )
            )

        return results

    @classmethod
    async def get_post_detail(
        cls,
        db: AsyncSession,
        user: User,
        post_id: uuid.UUID
    ) -> CommunityPostRead:
        stmt = (
            select(CommunityPost)
            .options(
                joinedload(CommunityPost.author_user).joinedload(User.profile),
                selectinload(CommunityPost.comments).joinedload(CommunityComment.author_user).joinedload(User.profile),
            )
            .where(CommunityPost.id == post_id)
        )
        res = await db.execute(stmt)
        post = res.scalar_one_or_none()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Community post not found.",
            )

        author_dto = cls._build_author_info(post.author_user)

        # Build comment hierarchy
        comment_dtos = []
        for c in (post.comments or []):
            if c.parent_comment_id is None:
                c_author = cls._build_author_info(c.author_user)
                comment_dtos.append(
                    CommunityCommentRead(
                        id=c.id,
                        post_id=c.post_id,
                        author=c_author,
                        parent_comment_id=c.parent_comment_id,
                        content=c.content,
                        created_at=c.created_at,
                        replies=[]
                    )
                )

        return CommunityPostRead(
            id=post.id,
            author=author_dto,
            title=post.title,
            content=post.content,
            post_type=post.post_type,
            tags=post.tags,
            upvotes_count=post.upvotes_count,
            created_at=post.created_at,
            comments_count=len(post.comments or []),
            comments=comment_dtos
        )

    @classmethod
    async def create_post(
        cls,
        db: AsyncSession,
        user: User,
        payload: CommunityPostCreate
    ) -> CommunityPostRead:
        post = CommunityPost(
            author_user_id=user.id,
            title=payload.title.strip(),
            content=payload.content.strip(),
            post_type=payload.post_type.upper().strip(),
            tags=payload.tags or []
        )
        db.add(post)
        await db.commit()
        await db.refresh(post)

        return await cls.get_post_detail(db, user, post.id)

    @classmethod
    async def update_post(
        cls,
        db: AsyncSession,
        user: User,
        post_id: uuid.UUID,
        payload: CommunityPostUpdate
    ) -> CommunityPostRead:
        stmt = select(CommunityPost).where(CommunityPost.id == post_id)
        res = await db.execute(stmt)
        post = res.scalar_one_or_none()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Community post not found.",
            )

        # IDOR check: author ownership
        if post.author_user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only edit your own posts.",
            )

        if payload.title:
            post.title = payload.title.strip()
        if payload.content:
            post.content = payload.content.strip()
        if payload.post_type:
            post.post_type = payload.post_type.upper().strip()
        if payload.tags is not None:
            post.tags = payload.tags

        await db.commit()
        return await cls.get_post_detail(db, user, post.id)

    @classmethod
    async def delete_post(
        cls,
        db: AsyncSession,
        user: User,
        post_id: uuid.UUID
    ) -> None:
        stmt = select(CommunityPost).where(CommunityPost.id == post_id)
        res = await db.execute(stmt)
        post = res.scalar_one_or_none()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Community post not found.",
            )

        # IDOR check: author ownership or admin role
        if post.author_user_id != user.id and user.role.upper() != "COLLEGE_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only delete your own posts.",
            )

        await db.delete(post)
        await db.commit()

    @classmethod
    async def get_comments(
        cls,
        db: AsyncSession,
        user: User,
        post_id: uuid.UUID
    ) -> List[CommunityCommentRead]:
        # Check post existence
        post_stmt = select(CommunityPost.id).where(CommunityPost.id == post_id)
        if not (await db.execute(post_stmt)).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Community post not found.",
            )

        stmt = (
            select(CommunityComment)
            .options(joinedload(CommunityComment.author_user).joinedload(User.profile))
            .where(CommunityComment.post_id == post_id)
            .order_by(CommunityComment.created_at.asc())
        )
        comments = (await db.execute(stmt)).scalars().all()

        return [
            CommunityCommentRead(
                id=c.id,
                post_id=c.post_id,
                author=cls._build_author_info(c.author_user),
                parent_comment_id=c.parent_comment_id,
                content=c.content,
                created_at=c.created_at,
                replies=[]
            ) for c in comments
        ]

    @classmethod
    async def create_comment(
        cls,
        db: AsyncSession,
        user: User,
        post_id: uuid.UUID,
        payload: CommunityCommentCreate
    ) -> CommunityCommentRead:
        # Check post existence
        post_stmt = select(CommunityPost).where(CommunityPost.id == post_id)
        post = (await db.execute(post_stmt)).scalar_one_or_none()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Community post not found.",
            )

        # Check parent comment if provided
        if payload.parent_comment_id:
            parent_stmt = select(CommunityComment).where(
                and_(CommunityComment.id == payload.parent_comment_id, CommunityComment.post_id == post_id)
            )
            if not (await db.execute(parent_stmt)).scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent comment not found on this post.",
                )

        comment = CommunityComment(
            post_id=post_id,
            author_user_id=user.id,
            parent_comment_id=payload.parent_comment_id,
            content=payload.content.strip()
        )
        db.add(comment)

        # Add notification to post author if commenter is different
        if post.author_user_id != user.id:
            notif = Notification(
                user_id=post.author_user_id,
                title="New Comment on Your Post",
                message=f"Someone commented on your post '{post.title[:40]}...'",
                notification_type="COMMUNITY_COMMENT"
            )
            db.add(notif)

        await db.commit()
        await db.refresh(comment)

        # Load author profile
        stmt_loaded = (
            select(CommunityComment)
            .options(joinedload(CommunityComment.author_user).joinedload(User.profile))
            .where(CommunityComment.id == comment.id)
        )
        loaded = (await db.execute(stmt_loaded)).scalar_one()

        return CommunityCommentRead(
            id=loaded.id,
            post_id=loaded.post_id,
            author=cls._build_author_info(loaded.author_user),
            parent_comment_id=loaded.parent_comment_id,
            content=loaded.content,
            created_at=loaded.created_at,
            replies=[]
        )

    @classmethod
    async def update_comment(
        cls,
        db: AsyncSession,
        user: User,
        comment_id: uuid.UUID,
        payload: CommunityCommentUpdate
    ) -> CommunityCommentRead:
        stmt = (
            select(CommunityComment)
            .options(joinedload(CommunityComment.author_user).joinedload(User.profile))
            .where(CommunityComment.id == comment_id)
        )
        comment = (await db.execute(stmt)).scalar_one_or_none()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found.",
            )

        # IDOR check
        if comment.author_user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only edit your own comments.",
            )

        comment.content = payload.content.strip()
        await db.commit()
        await db.refresh(comment)

        return CommunityCommentRead(
            id=comment.id,
            post_id=comment.post_id,
            author=cls._build_author_info(comment.author_user),
            parent_comment_id=comment.parent_comment_id,
            content=comment.content,
            created_at=comment.created_at,
            replies=[]
        )

    @classmethod
    async def delete_comment(
        cls,
        db: AsyncSession,
        user: User,
        comment_id: uuid.UUID
    ) -> None:
        stmt = select(CommunityComment).where(CommunityComment.id == comment_id)
        comment = (await db.execute(stmt)).scalar_one_or_none()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found.",
            )

        # IDOR check
        if comment.author_user_id != user.id and user.role.upper() != "COLLEGE_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only delete your own comments.",
            )

        await db.delete(comment)
        await db.commit()

    @classmethod
    async def get_peer_skill_requests(
        cls,
        db: AsyncSession,
        user: User,
        skill_id: Optional[uuid.UUID] = None,
        status_filter: Optional[str] = None,
        request_type: Optional[str] = None
    ) -> List[PeerSkillRequestRead]:
        stmt = (
            select(PeerSkillRequest)
            .options(
                joinedload(PeerSkillRequest.requester_student).joinedload(Student.user).joinedload(User.profile),
                joinedload(PeerSkillRequest.helper_student).joinedload(Student.user).joinedload(User.profile),
                joinedload(PeerSkillRequest.skill),
            )
        )

        if skill_id:
            stmt = stmt.where(PeerSkillRequest.skill_id == skill_id)
        if status_filter:
            stmt = stmt.where(PeerSkillRequest.status == status_filter.upper().strip())
        if request_type:
            stmt = stmt.where(PeerSkillRequest.request_type == request_type.upper().strip())

        stmt = stmt.order_by(desc(PeerSkillRequest.created_at))
        requests = (await db.execute(stmt)).scalars().all()

        results = []
        for req in requests:
            req_user_prof = req.requester_student.user.profile if (req.requester_student and req.requester_student.user and req.requester_student.user.profile) else None
            req_name = f"{req_user_prof.first_name} {req_user_prof.last_name}".strip() if req_user_prof else "Student"

            help_name = None
            if req.helper_student and req.helper_student.user and req.helper_student.user.profile:
                h_prof = req.helper_student.user.profile
                help_name = f"{h_prof.first_name} {h_prof.last_name}".strip()

            results.append(
                PeerSkillRequestRead(
                    id=req.id,
                    requester_student_id=req.requester_student_id,
                    requester_name=req_name,
                    helper_student_id=req.helper_student_id,
                    helper_name=help_name,
                    skill_id=req.skill_id,
                    skill_name=req.skill.name if req.skill else "Skill",
                    request_type=req.request_type,
                    description=req.description,
                    status=req.status,
                    created_at=req.created_at
                )
            )

        return results

    @classmethod
    async def get_peer_skill_request_detail(
        cls,
        db: AsyncSession,
        user: User,
        request_id: uuid.UUID
    ) -> PeerSkillRequestRead:
        stmt = (
            select(PeerSkillRequest)
            .options(
                joinedload(PeerSkillRequest.requester_student).joinedload(Student.user).joinedload(User.profile),
                joinedload(PeerSkillRequest.helper_student).joinedload(Student.user).joinedload(User.profile),
                joinedload(PeerSkillRequest.skill),
            )
            .where(PeerSkillRequest.id == request_id)
        )
        req = (await db.execute(stmt)).scalar_one_or_none()
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer skill request not found.",
            )

        req_user_prof = req.requester_student.user.profile if (req.requester_student and req.requester_student.user and req.requester_student.user.profile) else None
        req_name = f"{req_user_prof.first_name} {req_user_prof.last_name}".strip() if req_user_prof else "Student"

        help_name = None
        if req.helper_student and req.helper_student.user and req.helper_student.user.profile:
            h_prof = req.helper_student.user.profile
            help_name = f"{h_prof.first_name} {h_prof.last_name}".strip()

        return PeerSkillRequestRead(
            id=req.id,
            requester_student_id=req.requester_student_id,
            requester_name=req_name,
            helper_student_id=req.helper_student_id,
            helper_name=help_name,
            skill_id=req.skill_id,
            skill_name=req.skill.name if req.skill else "Skill",
            request_type=req.request_type,
            description=req.description,
            status=req.status,
            created_at=req.created_at
        )

    @classmethod
    async def create_peer_skill_request(
        cls,
        db: AsyncSession,
        user: User,
        payload: PeerSkillRequestCreate
    ) -> PeerSkillRequestRead:
        # Resolve student record for current user
        st_stmt = select(Student).where(Student.user_id == user.id)
        student = (await db.execute(st_stmt)).scalar_one_or_none()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authenticated student accounts can post peer skill exchange requests.",
            )

        # Validate skill reference
        sk_stmt = select(Skill).where(Skill.id == payload.skill_id)
        skill = (await db.execute(sk_stmt)).scalar_one_or_none()
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referenced skill does not exist in skill taxonomy.",
            )

        req = PeerSkillRequest(
            requester_student_id=student.id,
            skill_id=payload.skill_id,
            request_type=payload.request_type.upper().strip(),
            description=payload.description.strip(),
            status="OPEN"
        )
        db.add(req)
        await db.commit()
        return await cls.get_peer_skill_request_detail(db, user, req.id)

    @classmethod
    async def update_peer_skill_request(
        cls,
        db: AsyncSession,
        user: User,
        request_id: uuid.UUID,
        payload: PeerSkillRequestUpdate
    ) -> PeerSkillRequestRead:
        stmt = select(PeerSkillRequest).where(PeerSkillRequest.id == request_id)
        req = (await db.execute(stmt)).scalar_one_or_none()
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer skill request not found.",
            )

        # Get student context if available
        st_stmt = select(Student).where(Student.user_id == user.id)
        current_student = (await db.execute(st_stmt)).scalar_one_or_none()

        is_requester = current_student and (current_student.id == req.requester_student_id)
        is_helper = current_student and (payload.helper_student_id == current_student.id)

        # IDOR check: Only requester or accepting helper can update
        if not is_requester and not is_helper and user.role.upper() != "COLLEGE_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You cannot modify another student's peer skill request.",
            )

        if payload.status:
            req.status = payload.status.upper().strip()
        if payload.helper_student_id:
            req.helper_student_id = payload.helper_student_id
        if payload.description and is_requester:
            req.description = payload.description.strip()

        await db.commit()
        return await cls.get_peer_skill_request_detail(db, user, req.id)

    @classmethod
    async def get_activities(
        cls,
        db: AsyncSession,
        user: User,
        activity_type: Optional[str] = None
    ) -> List[ActivityRead]:
        stmt = (
            select(Activity)
            .options(
                joinedload(Activity.institution),
                joinedload(Activity.conducted_by_user).joinedload(User.profile),
            )
        )

        if activity_type:
            stmt = stmt.where(Activity.activity_type == activity_type.upper().strip())

        stmt = stmt.order_by(desc(Activity.start_time))
        activities = (await db.execute(stmt)).scalars().all()

        results = []
        for act in activities:
            c_name = None
            if act.conducted_by_user:
                c_prof = act.conducted_by_user.profile if hasattr(act.conducted_by_user, 'profile') and act.conducted_by_user.profile else None
                c_name = f"{c_prof.first_name} {c_prof.last_name}".strip() if c_prof else act.conducted_by_user.username

            results.append(
                ActivityRead(
                    id=act.id,
                    institution_id=act.institution_id,
                    institution_name=act.institution.name if act.institution else "Institution",
                    title=act.title,
                    description=act.description,
                    activity_type=act.activity_type,
                    start_time=act.start_time,
                    end_time=act.end_time,
                    location_or_url=act.location_or_url,
                    conducted_by_user_id=act.conducted_by_user_id,
                    conducted_by_name=c_name,
                    created_at=act.created_at
                )
            )

        return results
