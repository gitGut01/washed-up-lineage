import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DatamodelSearchComponent } from '../datamodel-search/datamodel-search.component';


@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, DatamodelSearchComponent],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  headerText: string = '';
  showBackArrow: boolean = false;
  objectId: string | null = null;
  showInfo: boolean = false;
  showSearch: boolean = false;

  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit(): void {
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.updateHeaderText();
        this.updateQueryParams();
      });
  }

  updateHeaderText(): void {
    const currentRoute = this.router.url.split('?')[0]; // Remove query params
    this.showBackArrow = currentRoute !== '/global-lineage';
    this.showSearch = currentRoute === '/global-lineage' || currentRoute === '/datamodel-lineage';
    
    switch (currentRoute) {
      case '/column-lineage':
        this.headerText = 'Column Lineage';
        break;
      case '/datamodel-lineage':
        this.headerText = 'Object Lineage';
        break;
      case '/global-lineage':
        this.headerText = 'Global Lineage';
        break;
      default:
        this.headerText = 'Default Header';
        break;
    }
  }

  updateQueryParams(): void {
    this.route.queryParams.subscribe(params => {
      this.objectId = params['object_id']|| null;
      this.showInfo = params['show_info'] === 'true';
    });
  }

  getBackQueryParams(): any {
    const queryParams: any = {};
    if (this.objectId) {
      queryParams['object_id'] = this.objectId;
    }
    if (this.showInfo) {
      queryParams['show_info'] = true;
    }
    return queryParams;
  }
}