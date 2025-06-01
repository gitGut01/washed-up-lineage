import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ColumnLineageComponent } from './column-lineage.component';

describe('ColumnLineageComponent', () => {
  let component: ColumnLineageComponent;
  let fixture: ComponentFixture<ColumnLineageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ColumnLineageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ColumnLineageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
