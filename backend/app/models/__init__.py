from app.models.base import Base, TimestampMixin
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student, Teacher, InstitutionStaff
from app.models.companies import Company, CompanyUser
from app.models.skills import Skill, SkillRelationship, StudentSkill, SkillEvidence
from app.models.careers import CareerRole, CareerRoleSkill, SkillGap, Roadmap, RoadmapItem
from app.models.assessments import Assessment, AssessmentQuestion, AssessmentAttempt
from app.models.training import TrainingProgram, TrainingEnrollment
from app.models.opportunities import Opportunity, OpportunitySkill, Application, ApplicationStatusHistory
from app.models.internships import Internship, InternshipProgress, InternshipEvaluation
from app.models.placements import PlacementRecord, PlacementInteraction
from app.models.portfolio import PortfolioItem, Recognition, ResumeVersion
from app.models.mentorship import MentorConnection, MentorshipSession
from app.models.community import CommunityPost, CommunityComment, PeerSkillRequest, Activity
from app.models.competitions import Competition, CompetitionParticipant, CompetitionTeam, CompetitionTeamMember
from app.models.notifications import Notification
from app.models.embeddings import Embedding

__all__ = [
    "Base",
    "TimestampMixin",
    # 1-2
    "User",
    "UserProfile",
    # 3-7
    "Institution",
    "Department",
    "Student",
    "Teacher",
    "InstitutionStaff",
    # 8-9
    "Company",
    "CompanyUser",
    # 10-13
    "Skill",
    "SkillRelationship",
    "StudentSkill",
    "SkillEvidence",
    # 14-18
    "CareerRole",
    "CareerRoleSkill",
    "SkillGap",
    "Roadmap",
    "RoadmapItem",
    # 19-21
    "Assessment",
    "AssessmentQuestion",
    "AssessmentAttempt",
    # 22-23
    "TrainingProgram",
    "TrainingEnrollment",
    # 24-27
    "Opportunity",
    "OpportunitySkill",
    "Application",
    "ApplicationStatusHistory",
    # 28-30
    "Internship",
    "InternshipProgress",
    "InternshipEvaluation",
    # 31-32
    "PlacementRecord",
    "PlacementInteraction",
    # 33-35
    "PortfolioItem",
    "Recognition",
    "ResumeVersion",
    # 36-37
    "MentorConnection",
    "MentorshipSession",
    # 38-41
    "CommunityPost",
    "CommunityComment",
    "PeerSkillRequest",
    "Activity",
    # 42-45
    "Competition",
    "CompetitionParticipant",
    "CompetitionTeam",
    "CompetitionTeamMember",
    # 46
    "Notification",
    # 47
    "Embedding",
]
