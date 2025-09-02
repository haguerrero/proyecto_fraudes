import { Component, ChangeDetectorRef } from '@angular/core';
import { JsonPipe, PercentPipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { FraudServicesService } from './services/fraud-services.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    JsonPipe,
    FormsModule,
    MatSlideToggleModule,
    PercentPipe,
    DecimalPipe,
    NgbTooltipModule,
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  dataPredict: {} = {};
  transactions: any[] = [];
  singleData: string = '';
  singleResult: any = {};
  batchResults: any = {};
  batchCount: number = 10;
  showSingleResult: boolean = false;
  showResults: boolean = false;

  /**
   * Example JSON for single transaction input
   */
  jsonExample: string = `Ejemplo de Json: \n\n{
        "TransactionID": "SIM000001",
        "step": 484,
        "type": "PAYMENT",
        "amount": 12492.87,
        "nameOrig": "C7038986",
        "oldbalanceOrg": 12969.04,
        "newbalanceOrg": 476.1700000000001,
        "nameDest": "C6952866",
        "oldbalanceDest": 0,
        "newbalanceDest": 12492.87,
        "isFraud": 0,
        "isFlaggedFraud": 0 \n}`;

  /**
   * Constructor
   * @param fraudService Service to interact with the backend API
   * @param cd ChangeDetectorRef to manually trigger change detection
   */
  constructor(
    private fraudService: FraudServicesService,
    private cd: ChangeDetectorRef
  ) {}

  /**
   * Author: Hugo Guerrero
   * Date: June 2024
   * email: hugoguerrero03@mail.com
   * Description: This Angular component interacts with a fraud detection backend API.
   * It provides functionalities for single and batch transaction predictions,
   * as well as generating simulated transactions. The component manages API responses,
   * and UI toggles to display results.
   */

  /**
   * Single Prediction
   * @param data JSON string of a single transaction
   */
  predict(data: any) {
    const parsed = JSON.parse(data);
    this.fraudService.predict(parsed).subscribe({
      next: (response) => {
        this.singleResult = { ...response };
      },
      error: (error) => {
        console.error('Error al realizar la predicción!', error);
      },
    });
  }

  /**
   * Batch Prediction
   * @param transactions  Array of transaction objects
   */
  predictBatch(transactions: any[]) {
    this.fraudService.predictBatch(transactions).subscribe({
      next: (response) => {
        this.batchResults = { ...response };
        this.cd.detectChanges();
      },
      error: (error) => {
        console.error('Error al realizar la predicción por lotes!', error);
      },
    });
  }

  /**
   * generate Transactions
   * @param arg Number of transactions to generate
   */
  getTransactions(arg: number) {
    this.fraudService.generateTransaction(arg).subscribe({
      next: (response) => {
        if (response) {
          this.predictBatch(response.transactions);
        }
      },
      error: (error) => {
        console.error('Error al generar las transacciones!', error);
      },
    });
  }

  /**
   * Toggle display of json of results
   * @param variableName Variable boolean to toggle
   */
  showResultsToggle(variableName: 'showResults' | 'showSingleResult') {
    this[variableName] = !this[variableName];
  }

  public copyExample() {
    this.singleData = this.jsonExample.replace(/^Ejemplo de Json:\s*/, '');

  }
}
