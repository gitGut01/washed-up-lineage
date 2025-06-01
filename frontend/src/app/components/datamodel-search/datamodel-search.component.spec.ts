import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatamodelSearchComponent } from './datamodel-search.component';

describe('DatamodelSearchComponent', () => {
  let component: DatamodelSearchComponent;
  let fixture: ComponentFixture<DatamodelSearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DatamodelSearchComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DatamodelSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
