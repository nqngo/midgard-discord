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

![Midgard-Discord Bot Architecture Diagram](https://www.plantuml.com/plantuml/svg/JL3BJiGm3BpxAwpUMUxLgbgn2pVWWFY0D76hgcsySX8u8FvzxJwadZAUcOwdlgJi99Tv0i_pdIF5ZDNx47eduOLpXIvXondyn2NWRKYU9HWPLWYRydcdg55-D8ttOHEhgptTv8JmW_8loxW4-mwSpopudKYCAFf2v41OlOQUlaX-I1PhO3-gvmyG3qMlRvXBZ3IPPuFm3y5brxgaARSDhHaj0DWAF3yr-m_KECHCeZtIhgdekrhtQ9pHcnFFfrDZnwZnUROB6QLbPXT30ygheR4b1XMjTPQSRkYB4ApCckExutWusVBraQbHDxYUK2Xn4Ky9BXH3cQS7)

1. Users will interface with the MidgardLab entirely through Discord slash commands.
2. The Discord bot will communicate with the OpenStack API on the users' behalf to setup an account, register public key and provision VM.
3. The Discord bot will also setup Cloudflare DNS tunnels to allow users to SSH into the VMs provisioned.

## Usage

Run the bot with the following command:

```bash
poetry run midgard
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## License
This project is licensed under the terms of the [MIT license](LICENSE).
