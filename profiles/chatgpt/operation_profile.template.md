# ChatGPT Operation Profile

## Endpoint

https://gateway.example.com

## Authentication

Authorization: Bearer <API_KEY>

## Allowed Operations

- Project List
- Branch List
- File Get
- File Create
- File Update
- Merge Request Create
- Issue Create

## Forbidden Operations

- branch delete
- project delete
- force push
- secret read
- CI/CD variable read
- GitLab admin API

## Allowed Projects

- LocalGitLabGateway

## Allowed Branches

- develop
- feature/*

## Allowed Paths

- docs/**
- README.md
- src/**
