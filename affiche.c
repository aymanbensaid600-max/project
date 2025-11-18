#include<stdio.h>
#include"fonction.h"
#include"structure.h"
void affiche(etudiant *d)
{int i;
for(i=0;i<2;i++)
     {printf("liste des donnée");
     printf(" les information personel de l'etudiant[ %s %s]\n",d[i]->nom,d[i]->prenom);
      printf("la date de naissance: %d/%d/%d \n",d[i]->naissance.jour, d[i]->naissance.mois,d[i]->naissance.annee);
       printf("la date d'inscription: %d/%d/%d \n",d[i]->inscription.jour,d[i]->inscription.mois,d[i]->inscription.annee);
       printf("filliére %s\n",d[i]->fil);
       printf("Moyenne %d\n",d[i]->moyenne);
     }
}
