<!-- omit in toc -->
# Contributing to Midgard Discord Bot

> And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support the project and show your appreciation, which we would also be very happy about:
> - Star the project
> - Refer this project in your project's readme
> - Mention the project at local meetups and tell your friends/colleagues

<!-- omit in toc -->
## Table of Contents

- [I Have a Question](#i-have-a-question)
- [I Want To Contribute](#i-want-to-contribute)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Improving The Documentation](#improving-the-documentation)

## I Have a Question

> If you want to ask a question, we assume that you have read the available [Documentation](https://docs.midgardlab.io).

Before you ask a question, it is best to search for existing [Issues](https://github.com/nqngo/midgard-discord/issues) that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue. It is also advisable to search the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/nqngo/midgard-discord/issues/new).
- Provide as much context as you can about what you're running into.

## I Want To Contribute

> ### Legal Notice <!-- omit in toc -->
> When contributing to this project, you must agree that you have authored 100% of the content, that you have the necessary rights to the content and that the content you contribute may be provided under the project license.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Midgard Discord Bot, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and the community to understand your suggestion and find related suggestions.

<!-- omit in toc -->
#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [documentation](https://docs.midgardlab.io) carefully and find out if the functionality is already covered, maybe by an individual configuration.
- Perform a [search](https://github.com/nqngo/midgard-discord/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to convince the project's developers of the merits of this feature. Keep in mind that we want features that will be useful to the majority of our users and not just a small subset.

<!-- omit in toc -->
#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/nqngo/midgard-discord/issues).

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point you can also tell which alternatives do not work for you.
- **Explain why this enhancement would be useful** to most Midgard Discord Bot users. You may also want to point out the other projects that solved it better and which could serve as inspiration.


### Your First Code Contribution

1. Fork the project to your own repository.
2. Make your changes in a new git branch:
```bash
git checkout -b my-fix-branch main
```
3. Install [Python 3.10](https://wiki.python.org/moin/BeginnersGuide/Download) or higher and [Poetry](https://python-poetry.org/docs/#installation).
```bash
sudo apt install python3.10
pip install poetry
```
4. Setup your Poetry development environment:
```bash
poetry env use python3.10
poetry install
pre-commit install
```
5. Run the bot:
```bash
poetry run midgard-bot
```

### Improving The Documentation
Documentation improvements are very welcome. If you want to help, please go to the [Documentation Repository](https://github.com/nqngo/midgard-docs) and follow the instructions there.
