def get_profile_path(instance, filename)
    dir = "/uploaded/%s/profile_pics/%s" % (instance.user, filename)
    return dir
