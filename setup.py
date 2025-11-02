#!/usr/bin/env python3

from setuptools import find_packages
from setuptools import setup

setup(
    name='workano-ai-agent-plugin',
    version='1.0',
    description='This is a plugin for AI Agent',
    author='workano team',
    author_email='info@workano.com',
    packages=find_packages(),
    url='https://workano.com',
    include_package_data=True,
    package_data={
        'workano_ai_agent_plugin': ['api.yml'],
    },

    entry_points={
        'wazo_calld.plugins': [
            'workano_ai_agent_plugin = workano_ai_agent_plugin.plugin:Plugin'
        ],
        'console_scripts': [
            'workano-ai-server = workano_ai_agent_plugin.cli:main'
        ],
    }
)
