import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DatamodelLineageComponent } from './components/datamodel-lineage/datamodel-lineage.component';
import { ColumnLineageComponent } from './components/column-lineage/column-lineage.component';

export const routes: Routes = [
  { path: '', redirectTo: '/datamodel-lineage', pathMatch: 'full' },
  { path: 'datamodel-lineage', component: DatamodelLineageComponent },
  { path: 'column-lineage', component: ColumnLineageComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}