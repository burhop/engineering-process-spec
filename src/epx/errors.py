"""Stable diagnostics; presentation belongs to the consuming application."""

from __future__ import annotations


class Problem(Exception):
    def __init__(self, code: str, category: str, requirement: str, message: str, **evidence):
        super().__init__(message)
        self.diagnostic = {
            "code": code, "category": category, "requirement": requirement,
            "message": message, **evidence,
        }


def invalid(code: str, requirement: str, message: str, **evidence) -> Problem:
    return Problem(code, "invalid", requirement, message, **evidence)


def unavailable(code: str, requirement: str, message: str, **evidence) -> Problem:
    return Problem(code, "unavailable", requirement, message, **evidence)
