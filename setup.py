#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-silent-hall-of-fame.jarbasai=skill_silent_hall_of_fame:SilentHallOfFameSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-silent-hall-of-fame',
    version='0.0.1',
    description='ovos silent movies skill plugin',
    url='https://github.com/JarbasSkills/skill-silent-hall-of-fame',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_silent_hall_of_fame": ""},
    package_data={'skill_silent_hall_of_fame': ['locale/*', 'res/*']},
    packages=['skill_silent_hall_of_fame'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
