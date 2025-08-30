import { Component, ChangeDetectorRef } from '@angular/core';
import { JsonPipe, PercentPipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

import { FraudServicesService } from './services/fraud-services.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    JsonPipe,
    FormsModule,
    MatSlideToggleModule,
    PercentPipe,
    DecimalPipe
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {

  dataPredict: {} = {};
  transactions: any[] = [];
  singleData: string = '';
  singleResult: any = {}
  batchResults: any = {}
  batchCount: number = 10;
  showSingleResult: boolean = false;
  showResults: boolean = false;

  constructor(
    private fraudService: FraudServicesService,
    private cd: ChangeDetectorRef
  ) {

  }


  predict(data: any) {
    const parsed = JSON.parse(data);
    this.fraudService.predict(parsed).subscribe({
      next: (response) => {
        this.singleResult = {...response};
      },
      error: (error) => {
        console.error('Error al realizar la predicción!', error);
      }
    });
  }

  predictBatch(transactions: any[]) {

    this.fraudService.predictBatch(transactions).subscribe({
      next: (response) => {
        this.batchResults = {...response};
        this.cd.detectChanges();
      },
      error: (error) => {
        console.error('Error al realizar la predicción por lotes!', error);
      }
    });
  }

    getTransactions(arg: number) {
    this.fraudService.generateTransaction(arg).subscribe({
      next: (response) => {
        if(response){
          this.predictBatch(response.transactions);
        }
      },
      error: (error) => {
        console.error('Error al generar las transacciones!', error);
      }
    });
  }

  showResultsToggle(variableName: 'showResults' | 'showSingleResult') {
  this[variableName] = !this[variableName];
}

}
