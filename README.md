# Midgard Discord bot

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/nqngo/midgard-discord/main.svg)](https://results.pre-commit.ci/latest/github/nqngo/midgard-discord/main) [![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)

**Midgard** is a private OpenStack cloud for VAIT testing, training, and development purpose. This project aims to simplify and allow quick provisioning of OpenStack VM using an opinionated workflow entirely through Discord, following a ChatOps model.

## Motivations
1. **Midgard** is an OpenStack lab running entirely on-premise. While it has NAT connectivity, the sticking point is how to direct ingress point to the VMs provisioned inside the lab.
2. For most teaching lab, the users do not deviate from a standard configuration.
3. The resource should be accessible to most users so beginners and professionals alike can quickly provision, experiment and shutdown their solutions.
4. We want to avoid running jumpboxes.
5. We want to avoid installing any VPN solution.
6. We want to avoid software client dependencies, access should simply be SSH into the VM.

## Software Architecture

The software architecture for the bot is as followed:

![Midgard-Discord Bot Architecture Diagram](https://www.plantuml.com/plantuml/svg/JP2zQiH038HxFOLmdqjl3dF97O4K-Mdo06kjR8ozgsD_I17oxbdPw-1AevdXG-WIamafkmL8t5qy-uJDssH74-opf0PDn5uIq2BPucsA9C6gQJS9DVcuioyecfy-NpMMVQzvSzKnB2OmldFwbZ2lR1h0K9A0Nv636hbCy68PcvlGp66jsLNY3o0Uxho-OChUywATAk4Nh4ccDr49LMsC7a3fU7xezlDRd7pYO2Z5FIiX3IsI59hQjOddqwdJLxJuwFG_Qf4uPxpjeFYbKB3zBkivBPQ26LbvmpJ2vcum6exhuMKRucZzOm97oO4u0bpOs-oMFm00)

1. Users will interface with the MidgardLab entirely through Discord slash commands.
2. The Discord bot will communicate with the OpenStack API on the users' behalf to setup an account, register public key and provision VM.
3. The Discord bot will also setup Cloudflare DNS tunnels to allow users to SSH into the VMs provisioned.

## Usage

Run the bot with the following command:

```bash
poetry run midgard
```
