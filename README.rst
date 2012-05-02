A PYPI cache, for those times when you're feeling down.

Goals:

1. Act as a straight proxy to PYPI, should be invisible. Aim to use mirrors if possible.
2. Cache packages in the specified directory as downloaded.
3. When a cached file is available use that instead.


1. Act as a proxy to PyPI when developing. Aim to cache packages as requested, which will allow for bandwidth savings and development time reduction.
    - Implicitly works as a proxy as PyPI urls returned are relative in a /simple page (DONE)
    - Fetch URL list from PyPI and use that instead of proxying /simple
    - For the moment can only deal with urls PyPI returns, be it PyPI or otherwise.

2. Act local only cache of the packages acquired via development for deployment and testing.
    - This is easy, simply have a /local prefix to force local only mode to operate purely out of local cache. (DONE)

3. Allow developer to cache all packages based on a requirements.txt. This means we can explicitly cache requirements as part of a build step.
    - Involves iterating over requirements and hitting the PyPI proxy above. (DONE via PUT)
    - Can potentially handle custom indexes but makes sense to punt to custom upload (if a developer wants to get complicated, well... ;)).

4. Allow developer to upload custom packages (be it private development packages or patches to other packages).
    - This can cater for completely home grown packages and funky dependencies not handled above.
    - Needs a form to handle this
    - Could implement upload API, but would want to be careful we don't upload private packages. (DONE via PUT)

Bugs:

1. eggs aren't handled properly (or rather binary packages)
