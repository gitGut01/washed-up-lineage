import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatamodelLineageComponent } from './datamodel-lineage.component';

describe('DatamodelLineageComponent', () => {
  let component: DatamodelLineageComponent;
  let fixture: ComponentFixture<DatamodelLineageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DatamodelLineageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DatamodelLineageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
