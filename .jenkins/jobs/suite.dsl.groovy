@GrabResolver('https://artifactory.tagged.com/artifactory/libs-release-local/')
@Grab('com.tagged.build:jenkins-dsl-common:0.1.18')

import com.tagged.build.common.*

def redis_project = new Project(
    jobFactory,
    [
        githubOwner: 'jdi-tagged',
        githubProject: 'redis',
        githubHost: 'github.com',
        hipchatRoom:'PetsDev',
        email: 'jirwin@tagged.com'
    ]
)
def redis = redis_project.downstreamJob(defaultRef: 'build-sentinel') {
    description "Builds our fork of redis-sentinel from https://github.com/jdi-tagged/redis"
    jdk 'default'
    label 'orc01'
    steps{
        shell '''bash << _EOF_
make distclean
rm -rf SOURCES SPECS BUILD BUILDROOT RPMS SRPMS
echo making directory "$SOURCES"
mkdir SOURCES
echo running tar
tar czf SOURCES/redis-sentinel-2.8.9.21027786.tar.gz --exclude .git --exclude SOURCES --transform 's/^\\./redis-sentinel-2.8.9.21027786/' .
echo workspace "$WORKSPACE"
rpmbuild \\
           --define "_topdir $WORKSPACE" \\
           --define "release `date +%Y%m%d%H%M%S`" \\
           --clean \\
           --ba utils/redis-sentinel.spec
_EOF_'''
    }
    triggers {
        githubPush()
        scm('5 * * * *')
    }
    publishers {          // mailer(String recipients, String dontNotifyEveryUnstableBuildBoolean = false, String sendToIndividualsBoolean = false)
        mailer(redis_project.notifyEmail, true, true)
        archiveArtifacts('RPMS/**/*.rpm')
    }
    hipchat(redis_project.hipchatRoom, false)
}
