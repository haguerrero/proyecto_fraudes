import { TestBed } from '@angular/core/testing';

import { FraudServicesService } from './fraud-services.service';

describe('FraudServicesService', () => {
  let service: FraudServicesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FraudServicesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
