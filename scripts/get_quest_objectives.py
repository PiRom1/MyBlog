from Blog.models import ObjectifQuest



def run():

    ObjectifQuest.objects.create(type = "hdv",
                                 n_min = 1,
                                 n_max = 4)
    
    ObjectifQuest.objects.create(type = "enjoy",
                                 n_min = 5, 
                                 n_max = 10)
    
    ObjectifQuest.objects.create(type = "recit",
                                 n_min = 1,
                                 n_max = 1)
    
    ObjectifQuest.objects.create(type = "jeu",
                                 n_min = 10,
                                 n_max = 20)
    
    ObjectifQuest.objects.create(type = "soundbox",
                                 n_min = 1,
                                 n_max = 1)
    
    ObjectifQuest.objects.create(type = "pari",
                                 n_min = 1,
                                 n_max = 1)
    
    ObjectifQuest.objects.create(type = "dw_arena",
                                 n_min = 1,
                                 n_max = 1)
    
