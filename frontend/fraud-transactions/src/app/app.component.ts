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
  singleData: any = {}
  singleResult: any = {}
  batchResults: any = {}
  batchCount: number = 10;
  showResults: boolean = false;

  constructor(
    private fraudService: FraudServicesService,
    private cd: ChangeDetectorRef
  ) {

  }


  predict(data: any) {
    this.fraudService.predict(data).subscribe({
      next: (response) => {
        console.log('Predicción realizada:', response);
      },
      error: (error) => {
        console.error('Error al realizar la predicción!', error);
      }
    });
  }

  predictBatch(transactions: any[]) {

    this.fraudService.predictBatch(transactions).subscribe({
      next: (response) => {
        console.log('Predicción por lotes realizada:', response);
        this.batchResults = {...response};
        this.cd.detectChanges();
      },
      error: (error) => {
        console.error('Error al realizar la predicción por lotes!', error);
      }
    });
  }

    getTransactions(arg: number) {
      console.log(arg);
    this.fraudService.generateTransaction(arg).subscribe({
      next: (response) => {
        if(response){
          console.log('Transacción generada:', response);
          this.predictBatch(response.transactions);
        }
      },
      error: (error) => {
        console.error('Error al generar las transacciones!', error);
      }
    });
  }

  showResultsToggle(){
    this.showResults = !this.showResults;
  }

}
