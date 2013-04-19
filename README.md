# ScraperWiki Classic

This code is a clone of the master branch of the [ScraperWiki repository on bitbucket](bitbucket.org/ScraperWiki/scraperwiki).


## Notes

When setting up the django db to run on postgres, the migrations might fail at 024.  If they do then the quickest workaround is to remove the code in the forward() method of the migration, replace it with pass and then

    psql scraperwiki
    drop table model_vaults cascade;
    drop table model_vault_members;
    
    