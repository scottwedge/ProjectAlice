from pathlib import Path

import requests
from requests.exceptions import HTTPError
import shutil

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from core.base.model.Version import Version

from core.base.model.ProjectAliceObject import ProjectAliceObject
from core.commons import constants
from typing import Optional


class SkillStore(ProjectAliceObject):

	def __init__(self):
		super().__init__(logDepth=3)


	@staticmethod
	def getSkillRepo(skillName: str) -> Optional[Repo]:
		skillPath = f'skills/{skillName}'
		try:
			repo = Repo(skillPath)
			repo.remotes['ProjectAlice']
			return repo
		except (InvalidGitRepositoryError, NoSuchPathError, KeyError):
			return None


	def installSkill(self, skillName: str, skillUrl=None) -> bool:
		skillUrl = skillUrl or f'https://github.com/project-alice-assistant/skill_{skillName}.git'
		skillPath = Path('skills') / skillName
		try:
			repo = Repo(str(skillPath))
			repo.remotes['ProjectAlice']
		except (InvalidGitRepositoryError, NoSuchPathError):
			try:
				req = requests.head(skillUrl, allow_redirects=True)
				req.raise_for_status()
				if skillPath.exists():
					shutil.rmtree(skillPath)

				repo = Repo.clone_from(
					url=skillUrl,
					to_path=str(skillPath))
				repo.remotes['origin'].rename('ProjectAlice')
			except (GitCommandError, HTTPError):
				self.logInfo(f'❓ Skill "{skillName}" is not available in the skill store. Deprecated or is it a dev skill?')
				return False
		except KeyError:
			repo.create_remote('ProjectAlice', skillUrl)
		self.logInfo(f'Skill "{skillName}"" successfully downloaded')
		return True


	@staticmethod
	def fetchSkillRemote(skillName: str):
		repo = SkillStore.getSkillRepo(skillName)
		repo.remotes['ProjectAlice'].fetch()


	def getSkillRemoteVersion(self, skillName: str) -> Optional[str]:
		repo = self.getSkillRepo(skillName)
		remoteReferences = repo.remotes['ProjectAlice'].refs
		del remoteReferences['HEAD']
		del remoteReferences['master']

		versions = []
		for remoteRef in remoteReferences:
			remoteVersion = Version(str(remoteRef).split('/')[-1])
			if remoteVersion.isVersionNumber and remoteVersion <= Version(constants.VERSION):
				versions.append(remoteVersion)

		try:
			return max(versions)
		except:
			return None


	def checkForSkillUpdate(self, skillName: str) -> bool:
		remoteVersion = self.getSkillRemoteVersion(skillName)
		if not remoteReference:
			return False

		repo = self.getSkillRepo(skillName)

		if repo.head.commit != repo.remotes['ProjectAlice'].refs[remoteVersion].commit:
			return True
		else:
			return False


	def updateSkill(self, skillName: str) -> bool:
		repo = self.getSkillRepo(skillName)
		repo.head.reset(
			commit=repo.remotes['ProjectAlice'].refs[maxVersion],
			index=True,
			working_tree=True)
