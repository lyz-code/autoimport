For a smother experience, you can run `autoimport` each time you save your file
in your editor.

# Vim

To integrate `autoimport` into Vim, I recommend using the [ale
plugin](https://github.com/dense-analysis/ale).

!!! note ""

    If you are new to ALE, check [this
    post](https://lyz-code.github.io/blue-book/linux/vim/vim_plugins/#ale).

There's a [pull request](https://github.com/dense-analysis/ale/pull/3409) open
to run `autoimport` automatically by default. Until it's merged you can either:

* Copy the `autoload/ale/fixers/autoimport.vim` file into your `fixers`
    directory and edit `autoload/ale/fix/registry.vim` to match the contents of
    the pull request.
* Use the `feat/add-autoimport-support` branch of my [ale
    fork](https://github.com/lyz-code/ale/tree/feat/add-autoimport-support) as
    your ale directory.
