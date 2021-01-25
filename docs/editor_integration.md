For a smother experience, you can run `autoimport` each time you save your file
in your editor or make a commit.

# [pre-commit](https://pre-commit.com/)

You can run `autoimport` before we do a commit using the
[pre-commit](https://pre-commit.com/) framework. If you don't know how to use
it, follow [these
guidelines](https://lyz-code.github.io/blue-book/devops/ci/#configuring-pre-commit).

You'll need to add the following lines to your project's
`.pre-commit-config.yaml` file.

```yaml
repos:
  - repo: https://github.com/lyz-code/autoimport/
    rev: master
    hooks:
      - id: autoimport
```

# Vim
...