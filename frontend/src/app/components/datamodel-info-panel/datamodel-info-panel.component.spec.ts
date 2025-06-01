import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatamodelInfoPanelComponent } from './datamodel-info-panel.component';

describe('DatamodelInfoPanelComponent', () => {
  let component: DatamodelInfoPanelComponent;
  let fixture: ComponentFixture<DatamodelInfoPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DatamodelInfoPanelComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DatamodelInfoPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
