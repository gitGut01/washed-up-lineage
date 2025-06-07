import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DatamodelLineageComponent } from './components/datamodel-lineage/datamodel-lineage.component';
import { ColumnLineageComponent } from './components/column-lineage/column-lineage.component';
import { GlobalLineageComponent } from './components/global-lineage/global-lineage.component';

export const routes: Routes = [
  { path: '', redirectTo: '/global-lineage', pathMatch: 'full' },
  { path: 'datamodel-lineage', component: DatamodelLineageComponent },
  { path: 'global-lineage', component: GlobalLineageComponent },
  { path: 'column-lineage', component: ColumnLineageComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}