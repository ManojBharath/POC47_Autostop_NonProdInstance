# Non-Prod EC2 Auto Stop/Start Service - Linux Setup Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
---

## Overview

This project provides automated management of AWS EC2 Non-Prod instances on Linux platforms:

- **`auto_stop_nonprod.py`** - Manual script to stop running Non-Prod instances
---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Account (ap-south-2)                     │
│                                                                  │
│  ┌──────────────────────┐        ┌──────────────────────┐      │
│  │  Prod EC2 Instance   │        │ Non-Prod EC2 Instance│      │
│  │  (Tag: Prod server)  │        │(Tag: Non-prod server)│      │
│  │  Manual Management   │        │  Auto Stop/Start      │      │
│  └──────────────────────┘        └──────────────────────┘      │
│           │                              │                      │
│           └──────────────┬───────────────┘                      │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                    AWS API (boto3)
                           │
                ┌──────────┴
                │                       
┌───────────────▼──────────┐
│  Linux Server/VM         │
│  ┌────────────────────┐  │
│  │ auto_stop_nonprod  │  │
│  │ .py (manual)       │  │
│  └────────────────────┘  │
│  ┌────────────────────┐  │
│  │ schedule_start_    │  │
│  │ stop_nonprod.py    │  │
│  │ (auto-scheduler)   │  │
│  └────────────────────┘  │
│  ┌────────────────────┐  │
│  │ nonprod_scheduler  │  │
│  │ .log (logs)        │  │
│  └────────────────────┘  │
└──────────────────────────┘
```
