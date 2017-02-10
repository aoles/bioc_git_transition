#!/usr/bin/env python
"""Bioconductor run git transition code.

This module assembles the functions from `git_script.py` and
`svn_dump.py` so that the Bioconductor SVN --> Git transition
can be run in a sequential manner.

Author: Nitesh Turaga
Ideas taken from Jim Hester's code in Bioconductor/mirror

Usage:
    `python run_transition.py`
"""

import git_script as gs
import svn_dump as sd
import os
import logging as log
log.basicConfig(filename='transition.log', level=log.DEBUG)
log.debug("Bioconductor Transition Log File: \n")


# TODO: make this a function with arguments
def run_transition():
    """Update SVN local dump and run gitify-bioconductor.

    Step 0: Create dump
    `svnadmin create bioconductor-svn-mirror`
    `svnrdump dump https://hedgehog.fhcrc.org/bioconductor |
                svnadmin load bioconductor-svn-mirror`

    This function runs the steps in order needed.
    Step 1: Define variables, and paths for SVN dump, remote_svn_repo,
            'git package local repo'.
    Step 2: Update SVN local dump
    Step 3: Add git remote path.
    Step 4: Add release branches to each package in 'git package local repo'
    """
    # Step 0
    svn_root = 'file:///home/nturaga/bioconductor-svn-mirror/'
    dump_location = "bioconductor-svn-mirror/"
    remote_svn_server = 'https://hedgehog.fhcrc.org/bioconductor'
    bioc_git_repo = "/packages"
    update_file = "updt.svn"

    # Log debug statements
    log.debug("svn_root %s: \n" % svn_root)
    log.debug("dump_location %s: \n" % dump_location)
    log.debug("remote_svn_server %s: \n" % remote_svn_server)
    log.debug("bioc_git_repo %s: \n" % bioc_git_repo)
    log.debug("update_file %s: \n" % update_file)

    if not os.path.isdir(bioc_git_repo):
        os.mkdir(bioc_git_repo)

    # Step 1: Initial set up, get list of packs from trunk
    package_url = os.path.join(svn_root, 'trunk', 'madman', 'Rpacks')
    packs = sd.get_pack_list(package_url)
    # Create a local dump of SVN packages in a location
    sd.svn_dump(svn_root, packs, bioc_git_repo)

    # Step 2: Update
    revision = sd.svn_get_revision(svn_root)
    sd.svn_dump_update(revision, remote_svn_server, svn_root,
                       update_file)
    sd.update_local_svn_dump(dump_location, update_file)

    # Step 4: Add release branches to all   packages
    gs.add_release_branches(svn_root, bioc_git_repo)

    # Step 5: Add commit history
    gs.add_commit_history(svn_root)

    # Step 3: Add git remote branch, to make git package act as a server
    remote_path = "nturaga@git.bioconductor.org:/packages/"
    os.chdir(bioc_git_repo)
    gs.add_remote(bioc_git_repo, remote_path)
    os.chdir("..")

    # Step 6: Make Git repo bare
    destination_dir = "/home/nturaga/packages"
    gs.create_bare_repos(bioc_git_repo, destination_dir)
    return


if __name__ == '__main__':
    run_transition()
