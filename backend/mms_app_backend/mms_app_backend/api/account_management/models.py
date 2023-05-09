from sqlalchemy import Column, Integer, Text, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from ..models import AbstractBaseModel
from ...configs.database_config import Base


class Profile(AbstractBaseModel):
    __tablename__ = 'profiles'
    profile_picture = Column(URLType, nullable=True)
    about = Column(Text, nullable=True)
    website = Column(URLType, nullable=True)
    social_links = relationship("SocialLink", back_populates='profile')
    location = relationship("Location", back_populates='profile', uselist=False)
    mentor = relationship("Mentor", back_populates='profile', uselist=False)
    mentor_manager = relationship("MentorManager", back_populates='profile', uselist=False)
    user = relationship("User", back_populates='profile')
    user_id = Column(Integer, ForeignKey("users.id"))


class SocialLink(AbstractBaseModel):
    __tablename__ = 'social_links'
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    url = Column(URLType)
    name = Column(String(255), unique=True)
    profile = relationship("Profile", back_populates='social_links')


class Location(AbstractBaseModel):
    __tablename__ = 'locations'
    city = Column(String)
    state = Column(String)
    country = Column(String)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship("Profile", back_populates='location')


class ProgramMentorAssociation(AbstractBaseModel):
    __tablename__ = 'program_mentor_association'
    program_id = Column(Integer, ForeignKey('programs.id'), primary_key=True)
    mentor_id = Column(Integer, ForeignKey('mentors.id'), primary_key=True)


class Program(AbstractBaseModel):
    __tablename__ = 'programs'
    name = Column(String)
    avatar = Column(URLType)
    description = Column(Text)
    mentors = relationship("Mentor", back_populates='programs', secondary="program_mentor_association")
    mentor_manager = relationship("MentorManager", back_populates='programs')
    mentor_manager_id = Column(Integer, ForeignKey('mentor_managers.id'))
    criteria = relationship("Criterion", back_populates='program')
    previous_abouts = relationship("About", back_populates='previous_programs', secondary="about_programs_associations")
    mentor_about = relationship("About", back_populates='program')

class Mentor(AbstractBaseModel):
    __tablename__ = 'mentors'
    about = Column(Text)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship("Profile", back_populates='mentor')
    programs = relationship("Program", back_populates='mentors', secondary="program_mentor_association")
    task = relationship("Task", back_populates='mentors')
    task_id = Column(Integer, ForeignKey('tasks.id'))


#
class MentorManager(AbstractBaseModel):
    __tablename__ = 'mentor_managers'
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship("Profile", back_populates='mentor_manager')
    about = Column(Text)
    programs = relationship("Program", back_populates='mentor_manager')
    task = relationship("Task", back_populates='mentor_managers')
    task_id = Column(Integer, ForeignKey('tasks.id'))


# The criteria used for selection into the program
class Criterion(AbstractBaseModel):
    __tablename__ = 'criteria'
    name = Column(String)
    description = Column(Text)
    program_id = Column(Integer, ForeignKey('programs.id'))
    program = relationship("Program", back_populates='criteria')


# Roles played by a given user type.
class Role(AbstractBaseModel):
    __tablename__ = 'roles'
    name = Column(String)
    description = Column(Text)
    abouts = relationship("About", back_populates='roles', secondary="about_role_associations")


class AboutRoleAssociation(Base):
    __tablename__ = 'about_role_associations'
    about_id = Column(Integer, ForeignKey('abouts.id'),primary_key=True)
    role = Column(Integer, ForeignKey('roles.id'),primary_key=True)


class AboutProgramsAssociation(Base):
    __tablename__ = 'about_programs_associations'
    program_id = Column(Integer, ForeignKey('programs.id'),primary_key=True)
    about_id = Column(Integer, ForeignKey('abouts.id'),primary_key=True)


class About(AbstractBaseModel):
    __tablename__ = 'abouts'
    bio = Column(Text)
    was_mentor = Column(Boolean, default=False)
    availability = Column(Boolean, default=True)
    experience_years = Column(Integer)
    previous_programs = relationship("Program", back_populates='previous_abouts',
                                     secondary='about_programs_associations')
    program = relationship("Program", back_populates='mentor_about')
    program_id = Column(Integer, ForeignKey("programs.id"))
    documents = relationship("Document", back_populates='about')
    roles = relationship("Role", back_populates='abouts', secondary='about_role_associations')


class Document(AbstractBaseModel):
    __tablename__ = 'documents'
    name = Column(String(256))
    url = Column(URLType)
    about = relationship("About", back_populates='documents')
    about_id = Column(Integer, ForeignKey('abouts.id'))
